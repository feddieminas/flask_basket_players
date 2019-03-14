import unittest
import customFuncs
import os, pymongo

class TestApp(unittest.TestCase):
    """
    Our test suite for flask app.py custom functions
    """
    
    def test_guest_login_flask_view(self):
        '''
        Test two random users entering in the website. randomUser1 enters twice.
        Last AssertEqual tests three username Ids in case the file created three random users (duplicated randomUser1 with UserId = 2), which would have been a test failed.
        '''
        fileLogs = 'logs.txt'
        fileExists = os.path.isfile(fileLogs)
        if fileExists == True: os.remove(fileLogs)
        username, password, action ="randomUser1", b"randomUserPass1", "login_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "set session['userID'] and session['msg'] and redirect(url_for('get_list'))")
        username, password, action ="randomUser1", b"randomUserPass1", "logout_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "Session delete and redirect(url_for('get_username'))")
        username, password, action ="randomUser2", b"randomUserPass2", "login_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "set session['userID'] and session['msg'] and redirect(url_for('get_list'))") 
        username, password, action ="randomUser2", b"randomUserPass2", "logout_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "Session delete and redirect(url_for('get_username'))")        
        username, password, action ="randomUser1", b"randomUserPass1", "login_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "set session['userID'] and session['msg'] and redirect(url_for('get_list'))")
        username, password, action ="", "", "login_action"
        self.assertEqual(customFuncs.insert_login(username,password,action), "redirect(url_for('get_username'))")        
        with open(fileLogs, 'r') as f:
            lines = f.read().splitlines()
            f.close()
        lines = [item for i, text in enumerate(lines) for item in text.split(',')]
        # >>> ['0', 'randomuser1', '$2b$12$pCbYhaMxMZq3V1tUq3ZHu.gpLDHueM.4wKY/DwkfxmNDyT2szuMzO', '1', 'randomuser2', '$2b$12$sRU64dR3lnbvdrHAK0nt7.PzMqMDIpv32KmRzD/goOO09BaGjCeG6']
        self.assertEqual(list(filter(lambda x: x in ['0','1','2'], lines)), ['0','1'])
        
        """
        Run Test All Success
        """    
    
    def test_for_input_numbers_on_playerforms(self):
        '''
        guests can rate the discipline up to the number of 10 with max one decimal. Virtuals can rate them up to 20 with max one decimal.
        need to check for correct and not inputs in those fields
        '''
        #a) check proper whole numbers
        dictCheckVal = { "disc1_rate":"8", "disc2_rate":"9", "disc3_rate":"7", "vp_time":"2"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 8, 'vp_time': 2, 'disc2_rate': 9, 'disc3_rate': 7}
        self.assertIsInstance(dictCheckValTest['disc1_rate'], int)
        
        #b) check whole and float numbers with one decimal (allowed) and exceeded ones (we trim them) 
        dictCheckVal = { "disc1_rate":"8", "disc2_rate":"9.287", "disc3_rate":"9.5", "vp_time":"3.456"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 8, 'vp_time': 3.4, 'disc2_rate': 9.2, 'disc3_rate': 9.5}
        self.assertIsInstance(dictCheckValTest['vp_time'], float), self.assertNotEqual(str(dictCheckValTest['disc2_rate']), dictCheckVal['disc2_rate'])
        
        #c) check empty and float numbers with one decimal (allowed) and exceeded ones (we trim them) 
        dictCheckVal = { "disc1_rate":"8.86", "disc2_rate":"9.2", "disc3_rate":"", "vp_time":"3.3"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 8.8, 'vp_time': 3.3, 'disc2_rate': 9.2, 'disc3_rate': ''}
        self.assertEqual(float(dictCheckVal['disc1_rate'][:3]),dictCheckValTest['disc1_rate'])
        self.assertEqual([dictCheckValTest['disc3_rate'],dictCheckValTest['disc2_rate'],dictCheckValTest['vp_time']] , ["",9.2,3.3])
        
        #d) concept like b) 
        dictCheckVal = { "disc1_rate":"8.1", "disc2_rate":"9.0", "disc3_rate":"10.8645", "vp_time":"15.6"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 8.1, 'vp_time': 15.6, 'disc2_rate': 9.0, 'disc3_rate': 10.0}
        self.assertListEqual([dictCheckValTest['disc1_rate'],dictCheckValTest['disc2_rate'],dictCheckValTest['disc3_rate'],dictCheckValTest['vp_time']] , [8.1,9.0,10.0,15.6])
        
        #d) concept like c) 
        dictCheckVal = { "disc1_rate":"11.645", "disc2_rate":"9,287", "disc3_rate":"", "vp_time":"13.365"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 10, 'vp_time': 13.3, 'disc2_rate': 9.2, 'disc3_rate': ''}
        self.assertListEqual([dictCheckValTest['disc1_rate'],dictCheckValTest['disc2_rate'],dictCheckValTest['disc3_rate'],dictCheckValTest['vp_time']] , [10,9.2,'',13.3])
        
        #e) check values inserted as strings... insert min value for vo_time and average on discipline rate
        dictCheckVal = { "disc1_rate":"8.6", "disc2_rate":"9", "disc3_rate":"string", "vp_time":"string"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])
        # >>> {'disc1_rate': 8.6, 'vp_time': 0, 'disc2_rate': 9, 'disc3_rate': 5}
        self.assertNotIsInstance(dictCheckValTest['disc3_rate'], str), self.assertEqual(dictCheckValTest['vp_time'],0)
        
        #f) check values exceed the threshold
        dictCheckVal = { "disc1_rate":"18.6", "disc2_rate":"13", "disc3_rate":"20", "vp_time":"25.3"}
        dictCheckValTest = customFuncs.checkVals(dictCheckVal["disc1_rate"],dictCheckVal["disc2_rate"],dictCheckVal["disc3_rate"],dictCheckVal["vp_time"])  
        # >>> {'disc1_rate': 10, 'vp_time': 20, 'disc2_rate': 10, 'disc3_rate': 10}
        self.assertEqual(dictCheckValTest['disc3_rate'],10), self.assertEqual(dictCheckValTest['vp_time'],20)

        """
        Run Test All Success
        """
    
    def test_for_discipline_duplicates_to_be_distinct(self):
        '''
        As three disciplines are chosen where one can choose, accidentally one can insert two values the same.
        To be user friendly, we would try to avoid that  
        '''
        myDiscDict = {"disc1": "points", "disc2": "rebounds","disc3": "steals"}    
        dictCheckSel = customFuncs.checkSelects(myDiscDict.get("disc1", ""),myDiscDict.get("disc2", ""),myDiscDict.get("disc3", ""))
        self.assertDictEqual(myDiscDict, dictCheckSel)
        myDiscDict = {"disc1": "points", "disc2": "rebounds","disc3": "points"} 
        dictCheckSel = customFuncs.checkSelects(myDiscDict.get("disc1", ""),myDiscDict.get("disc2", ""),myDiscDict.get("disc3", "")) 
        self.assertNotIn("points", dictCheckSel["disc3"])
        myDiscDict = {"disc1": "points", "disc2": "","disc3": "steals"} 
        dictCheckSel = customFuncs.checkSelects(myDiscDict.get("disc1", ""),myDiscDict.get("disc2", ""),myDiscDict.get("disc3", ""))  
        self.assertIs(dictCheckSel["disc2"],"")
        myDiscDict = {"disc1": "points", "disc2": "steals","disc3": "steals"}
        dictCheckSel = customFuncs.checkSelects(myDiscDict.get("disc1", ""),myDiscDict.get("disc2", ""),myDiscDict.get("disc3", ""))  
        self.assertEqual(dictCheckSel["disc3"],"")

        """
        Run Test All Success
        """
    
    def test_virtual_place_time_if_one_is_empty(self):
        """
        Virtuals have two fields. In case one inserts a value in either one of the
        fields rather than both, have a friendly minimum input str/val in the empty field
        except if an na is designated on virtual place
        vp values are ["coffee", "brunch", "street","na"]
        """
        #a) min. virtual times
        vp, dictCheckVal = "brunch", {"vp_time":0}
        vpTest, dictCheckValTest = customFuncs.vpStandalone(vp,dictCheckVal)
        self.assertTrue(dictCheckValTest["vp_time"])
        #b)
        vp, dictCheckVal = "", {"vp_time":""}
        vpTest, dictCheckValTest = customFuncs.vpStandalone(vp,dictCheckVal) 
        self.assertFalse(dictCheckValTest["vp_time"])
        #c) min. virtual place
        vp, dictCheckVal = "", {"vp_time":5}
        vpTest, dictCheckValTest = customFuncs.vpStandalone(vp,dictCheckVal)        
        self.assertEqual("street", vpTest)
        
        """
        Run Test All Success
        """
    
    def test_name_insert_not_only_using_space(self):
        """
        Assuming that the Surname of a player will exist in only single Input Name field
        we try various combinations one would insert any one 
        """
        NamesList = ["Jordan","Michael Jordan","Michael.Jordan", "Michael,Jordan"]
        while NamesList:
            nameCFunc = customFuncs.playerHypothSurname(NamesList.pop(0))
            self.assertEqual("Jordan", nameCFunc)
        
        """
        Run Test All Success
        """
        
    def test_can_create_a_long_substr(self):
        """
        Test to see if we create a substr with min sufficient chars for mongo 
        regex to retrieve the closest match up Surname
        """
        SurnameList = ["Law", "Peri","Jordan", "Antetokoumpo"]
        while SurnameList:
            Surname = SurnameList.pop(0)
            wordLen = len(Surname)
            result = customFuncs.LongestSubstring(Surname,wordLen)
            self.assertGreater(len(result),3)
            self.assertIn(result,Surname)
            
        """
        FAILED (failures=1)
        
        PERSONAL NOTE: One failure occur due to name Law take the whole str as substr to retrieve. Its length 3 is not more than 3
        """
        
    def test_player_exists_in_db(self):
        '''
        Check if add or edit player name already exists in the database. We assume that not two players have same name and surname.
        the test is if player does not exists. If this returns to false, the player does exists. If it returns to True, the player does not
        exist.
        '''
        MONGODB_URI_TEST = 'mongodb://root:dcd_basketball1234@ds119049.mlab.com:19049/dcd_basketball'
        DBS_NAME = 'dcd_basketball'
        COLLECTION_NAME = 'users_basket_players'
        
        def mongo_connect(url):
            try:
                conn = pymongo.MongoClient(url)
                return conn
            except pymongo.errors.ConnectionFailure as e:
                pass
                
        conn = mongo_connect(MONGODB_URI_TEST) 
        ubp = conn[DBS_NAME][COLLECTION_NAME]
        
        self.assertFalse(customFuncs.CheckPlayerInDB(ubp, "luca doncic".lower(), 0)) 
        self.assertFalse(customFuncs.CheckPlayerInDB(ubp, "luca doncik".lower(), 0)) # max one spelling error of the above name
        self.assertTrue(customFuncs.CheckPlayerInDB(ubp, "ming".lower(), 0)) # only surname of the player
        self.assertFalse(customFuncs.CheckPlayerInDB(ubp, "yao ming".lower(), 0)) # name and surname of the player match
        
        """
        Run Test All Success
        """  
        
        '''
        python3 -m unittest
        F......
        ======================================================================
        FAIL: test_can_create_a_long_substr (test_customFuncs.TestApp)
        ----------------------------------------------------------------------
        Traceback (most recent call last):
          File "/home/ubuntu/workspace/tests/test_customFuncs.py", line 163, in test_can_create_a_long_substr
            self.assertGreater(len(result),3)
        AssertionError: 3 not greater than 3
        
        ----------------------------------------------------------------------
        Ran 7 tests in 1.460s
        
        FAILED (failures=1)        
        '''