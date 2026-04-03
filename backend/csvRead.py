import pandas as pd
import numpy as np

class User:
    def __init__(self, userNumber):
        self.userNumber = userNumber

        self.department = "N/A"

#The scores the user scored in various categories. Index 0 is knowledge, 1 is attitude, 2 is behaviour. Each out of 15.

        self.passwordScores = np.array([0, 0, 0])       #password managment scores
        self.emailScores = np.array([0, 0, 0])          #email use scores
        self.internetScores = np.array([0, 0, 0])       #internet use scores
        self.mobileScores = np.array([0, 0, 0])         #mobile computing scores
        self.socialScores = np.array([0, 0, 0])         #social network scores
        self.incidentScores = np.array([0, 0, 0])       #incident reporting scores
        self.infomationScores = np.array([0, 0, 0])     #infomation handling scores

#Return a numpy array of 3 elements for a certain category, each being a percentage score from 0 to 1. 
#Index 0 is knowledge score, 1 is attitude score, 2 is behaviour score.
    def getPasswordScores(self):
        return (self.passwordScores / 15)
    
    def getEmailScores(self):
        return (self.emailScores / 15)
    
    def getInternetScores(self):
        return (self.internetScores / 15)
    
    def getMobileScores(self):
        return (self.mobileScores / 15)
    
    def getSocialScores(self):
        return (self.socialScores / 15)
    
    def getIncidentScores(self):
        return (self.incidentScores / 15)
    
    def getInfomationScores(self):
        return (self.infomationScores / 15)

#Return the total score as a percentage from a certain category.
    def getTotalPasswordScore(self):
        return np.sum(self.passwordScores) / 45
    
    def getTotalEmailScore(self):
        return np.sum(self.emailScores) / 45
    
    def getTotalInternetScore(self):
        return np.sum(self.internetScores) / 45
    
    def getTotalMobileScore(self):
        return np.sum(self.mobileScores) / 45
    
    def getTotalSocialScore(self):
        return np.sum(self.socialScores) / 45
    
    def getTotalIncidentScore(self):
        return np.sum(self.incidentScores) / 45
    
    def getTotalInfomationScore(self):
        return np.sum(self.infomationScores) / 45
    
#Return the total score as a percentage attained across all categories, from either knowledge, attitude, or behaviour 
    def getTotalKnowledgeScore(self):
        return (self.passwordScores[0] + self.emailScores[0] + self.internetScores[0] + self.mobileScores[0] 
            + self.socialScores[0] + self.incidentScores[0] + self.infomationScores[0]) / 105
    
    def getTotalAttitudeScore(self):
        return (self.passwordScores[1] + self.emailScores[1] + self.internetScores[1] + self.mobileScores[1] 
            + self.socialScores[1] + self.incidentScores[1] + self.infomationScores[1]) / 105
    
    def getTotalBehaviourScore(self):
        return (self.passwordScores[2] + self.emailScores[2] + self.internetScores[2] + self.mobileScores[2] 
            + self.socialScores[2] + self.incidentScores[2] + self.infomationScores[2]) / 105
    
#Return the total overall score as a percentage
    def getTotalOverallScore(self):
        return (np.sum(self.passwordScores) + np.sum(self.emailScores) + np.sum(self.internetScores) + np.sum(self.mobileScores) 
            + np.sum(self.socialScores) + np.sum(self.incidentScores) + np.sum(self.infomationScores)) / 315
    
    def __str__(self):
        return "User " + str(self.userNumber)


#If the question is worded negatively, adjust scoring appropiately. Give indexes for questions which must be adjusted
def reverseScore(questionIndexs, data):

    for user in data:

        for index in questionIndexs:
            reversedScore = 6 - user[index + 1]
            user[index + 1] = reversedScore


#Read data and convert to numpy
def readData(csv):

    df = pd.read_csv(csv)
    data = df.to_numpy(na_value=None)

    #Turn reponse string into integer score (eg "2 - Disagree" --> 2)
    for user in data:
        for i in range(1, len(user)):
            try:
                user[i] = int(user[i][0])
            except TypeError:  # The original survey uses "2 - Disagree" for scoring, the AI survey uses just "2", this handles both.
                user[i] = int(user[i])

    #Indexes of questions which are negatively worded, so reverse the scoring
    questionIndexsToReverse = [1,10,11,14,17,18,21,22,26,28,29,33,39,40,44,48,49,55,58,59,60,62]  
    reverseScore(questionIndexsToReverse, data)

    return data

#Extract the user's scores from the data, return a list of user objects
def readUserScores(data):

    users = []
    userNumber = 0
    for currentUser in data:

        userNumber = userNumber + 1
        user = User(userNumber)
        users.append(user)

        #Get the user's department
        user.department = currentUser[0]

        #Get the user's password management scores
        user.passwordScores[0] = np.sum(currentUser[1:16:7])
        user.passwordScores[1] = np.sum(currentUser[22:37:7])
        user.passwordScores[2] = np.sum(currentUser[43:58:7])

        #Get the user's email use scores
        user.emailScores[2] = np.sum(currentUser[2:17:7])
        user.emailScores[1] = np.sum(currentUser[23:38:7])
        user.emailScores[0] = np.sum(currentUser[44:59:7])

        #Get the user's internet use scores
        user.internetScores[0] = np.sum(currentUser[3:18:7])
        user.internetScores[2] = np.sum(currentUser[24:39:7])
        user.internetScores[1] = np.sum(currentUser[45:60:7])

        #Get the user's mobile use scores
        user.mobileScores[1] = np.sum(currentUser[4:19:7])
        user.mobileScores[0] = np.sum(currentUser[25:40:7])
        user.mobileScores[2] = np.sum(currentUser[46:61:7])

        #Get the user's social network use scores
        user.socialScores[1] = np.sum(currentUser[5:20:7])
        user.socialScores[2] = np.sum(currentUser[26:41:7])
        user.socialScores[0] = np.sum(currentUser[47:62:7])

        #Get the user's incident reporting scores
        user.incidentScores[2] = np.sum(currentUser[6:21:7])
        user.incidentScores[1] = np.sum(currentUser[27:42:7])
        user.incidentScores[0] = np.sum(currentUser[48:63:7])

        #Get the user's infomation handling scores
        user.infomationScores[0] = np.sum(currentUser[7:22:7])
        user.infomationScores[2] = np.sum(currentUser[28:43:7])
        user.infomationScores[1] = np.sum(currentUser[49:64:7])

    return users

def updateSurveyResults(data, concern_rating, concern_rating_severe):
    data = readData(data)
    users = readUserScores(data)

    totalKnowledge = 0
    totalAttitude = 0
    totalBehaviour = 0

    result = {}
    categories = ["Knowledge", "Attitude", "Behaviour"]
    rows = ["Password Management", "Email Usage", "Internet Use", "Mobile Computing", "Social Networking", "Incident Reporting", "Information Handling"]
    overall_scores = [{}, {}, {}]
    areas_of_concern_ratings = {}
    employee_risk_level = [0] * 5
    departments = {}
    score_total = 0
    good_employee_number = 0
    result["column"] = categories
    result["row"] = rows
    result["areas_of_concern_ratings"] = areas_of_concern_ratings
    result["employee_risk_level"] = employee_risk_level
    result["departments"] = departments

    for user in users:
        mapping = {
            "Password Management": (user.passwordScores, user.getPasswordScores()),
            "Email Usage": (user.emailScores, user.getEmailScores()),
            "Internet Use": (user.internetScores, user.getInternetScores()),
            "Mobile Computing": (user.mobileScores, user.getMobileScores()),
            "Social Networking": (user.socialScores, user.getSocialScores()),
            "Incident Reporting": (user.incidentScores, user.getIncidentScores()),
            "Information Handling": (user.infomationScores, user.getInfomationScores())
        }

        for row in mapping:
            for i in range(len(overall_scores)):
                if row not in overall_scores[i]:
                    overall_scores[i][row] = {"value": 0, "count": 0}
                overall_scores[i][row]["value"] += int(mapping[row][0][i])
                overall_scores[i][row]["count"] += 1

            if row not in areas_of_concern_ratings:
                areas_of_concern_ratings[row] = {"value": 0, "count": 0}
            areas_of_concern_ratings[row]["value"] += int(np.sum(mapping[row][1]))
            areas_of_concern_ratings[row]["count"] += 3

        user_score = round(user.getTotalOverallScore() * 5)
        employee_risk_level[5-user_score] += 1

        totalKnowledge = totalKnowledge + user.getTotalKnowledgeScore()
        totalAttitude = totalAttitude + user.getTotalAttitudeScore()
        totalBehaviour = totalBehaviour + user.getTotalBehaviourScore()

        score_total += user.getTotalOverallScore()

        if (user.getTotalOverallScore() > 0.6):
            good_employee_number = good_employee_number + 1

        if user.department not in departments:
            departments[user.department] = {"value": 0, "count": 0}
        departments[user.department]["value"] += user.getTotalOverallScore()
        departments[user.department]["count"] += 1

    for row in rows:
        for i in range(len(overall_scores)):
            if row in overall_scores[i]:
                overall_scores[i][row] = round(overall_scores[i][row]["value"] / (overall_scores[i][row]["count"] * 3))
        areas_of_concern_ratings[row] = areas_of_concern_ratings[row]["value"] / areas_of_concern_ratings[row]["count"]

    if len(users) != 0:
        averageKnowledge = (totalKnowledge / len(users)) * 100
        averageAttitude = (totalAttitude / len(users)) * 100
        averageBehaviour = (totalBehaviour / len(users)) * 100
    else:
        averageKnowledge, averageAttitude, averageBehaviour = 0, 0, 0

    result["averageKnowledge"] = int(averageKnowledge * 1.25 - 25)
    result["averageAttitude"] = int(averageAttitude * 1.25 - 25)
    result["averageBehaviour"] = int(averageBehaviour * 1.25 - 25)

    result["overall"] = {}
    for i, c in enumerate(categories):
        result["overall"][c] = overall_scores[i]

    good_employee_percent = round((good_employee_number / len(users)) * 100) if len(users) > 0 else 100
    score_percent = round((score_total / len(users)) * 100) if len(users) > 0 else 100
    result["good_employee_percent"] = good_employee_percent
    result["risk_percent"] = 100 - (score_percent * 1.25 - 25) 

    result["areas_of_concern"] = []
    for area in areas_of_concern_ratings:
        score = areas_of_concern_ratings[area]
        if score < concern_rating_severe:
            severe = True
        else:
            severe = False
        if score < concern_rating:
            result["areas_of_concern"].append({"name": area, "severe": severe})

    best_dept = None
    worst_dept = None
    for dept in departments:
        departments[dept] = departments[dept]["value"] / departments[dept]["count"]
        if best_dept is None or worst_dept is None:
            best_dept = dept
            worst_dept = dept
        else:
            if departments[dept] > departments[best_dept]:
                best_dept = dept
            if departments[dept] < departments[worst_dept]:
                worst_dept = dept
        departments[dept] = round(departments[dept] * 5)
    result["best_dept"] = "N/A" if best_dept is None else best_dept
    result["worst_dept"] = "N/A" if worst_dept is None else worst_dept

    return result


if __name__ == "__main__":
    updateSurveyResults("Computer Security Survey.csv", 0.4, 0.6)