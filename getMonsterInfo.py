import requests

def monsterLinkDictionary():
    url = "https://www.aidedd.org/monster-dnd5/"
    textRecord = False

    data = '''{selections:[]
    }'''
    response = requests.post(url, data)
    t = response.text
    t = t[:t.find('<div class="display nocel">')]
    tSplit = t.split(">")
    validList = []
    lastLink = False
    for i in range(len(tSplit)):
        if lastLink:
            validList += [tSplit[i][:tSplit[i].find('<')]]
        if "<a href=" in tSplit[i]:
            validList += [tSplit[i][tSplit[i].find("<a href=") + len("<a href="):tSplit[i].find("target")]]
            lastLink = True
        else:
            lastLink = False

    if textRecord:
        s = ""
    monsterDict = {}
    lastIsMonsterLink = False
    lastLink = ""
    for ts in validList:
        if len(ts) > 0:
            stripped = ts.strip()
            if len(stripped) > 0:
                if lastIsMonsterLink:
                    if textRecord:
                        s += stripped
                    monsterDict[stripped] = lastLink
                if "'../dnd/monstres" == stripped[:len("'../dnd/monstres")]:
                    if textRecord:
                        s += stripped
                        s += "\t"
                    lastIsMonsterLink = True
                    lastLink = stripped[3:-1]
                elif textRecord:
                    s += "\n"
    if textRecord:        
        open("monsterInfo.txt", "w").write(s)
    return monsterDict

monsterDict = monsterLinkDictionary()

def getMonsterInfo(monster):
    if monster in monsterDict:
        url = "https://www.aidedd.org" + monsterDict[monster]
        data = '''{selections:[]
        }'''
        response = requests.post(url, data)
        t = response.text
        tSplit = t.split(">")
        nonBlank = []
        for i in range(len(tSplit)):
            tSplit[i] = tSplit[i][:tSplit[i].find("<")]
            stripped = tSplit[i].strip()
            if len(stripped) > 0:
                if stripped != ".":
                    nonBlank += [stripped]
        nonBlank = nonBlank[nonBlank.index(monster):]
        stats = {"AC":0,
                 "HP":0,
                 "Speed":{
                    "Land":0,
                    "Fly":0,
                    "Swim":0
                    },
                 "Abilities":{
                    "Scores":
                        {"STR":0,
                        "DEX":0,
                        "CON":0,
                        "INT":0,
                        "WIS":0,
                        "CHA":0},
                    "Bonuses":
                        {"STR":0,
                        "DEX":0,
                        "CON":0,
                        "INT":0,
                        "WIS":0,
                        "CHA":0},
                    "Saves":
                        {"STR":0,
                        "DEX":0,
                        "CON":0,
                        "INT":0,
                        "WIS":0,
                        "CHA":0}
                    },
                "Attacks":{
                    "Melee":[],
                    "Ranged":[]
                },
                "Spells":[],
                "Spell Save DC": 0,
                "Spell Slots":[],
                "Senses": {

                }
                }
        passedCR = False
        passedSpellCasting = False
        passedActions = False
        for i in range(len(nonBlank)):
            section = nonBlank[i]
            if i > 0:
                if nonBlank[i - 1] == "Challenge":
                    passedCR = True
            if section in ["Innate Spellcasting", "Spellcasting"]:
                passedSpellCasting = True
            if section == "Actions":
                passedActions = True
            if not passedCR:
                if section == "Armor Class":
                    stats["AC"] = int(nonBlank[i + 1][:nonBlank[i + 1].find("(")].strip())
                elif section == "Hit Points":
                    stats["HP"] = int(nonBlank[i + 1][:nonBlank[i + 1].find("(")].strip())
                elif section == "Speed":
                    if "," in nonBlank[i + 1]:
                        speeds = nonBlank[i + 1].split(",")
                        for speed in speeds:
                            if "fly" in speed:
                                stats["Speed"]["Fly"] = int(speed[speed.find("fly") + 3:speed.find("ft")].strip())
                            elif "swim" in speed:
                                stats["Speed"]["Swim"] = int(speed[speed.find("swim") + 4:speed.find("ft")].strip())
                            else:
                                stats["Speed"]["Land"] = int(speed[:speed.find("ft")].strip())
                    else:
                        speed = nonBlank[i + 1]
                        stats["Speed"]["Land"] = int(speed[:speed.find("ft")].strip())
                elif section in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
                    stats["Abilities"]["Scores"][section] = int(nonBlank[i + 1][:nonBlank[i + 1].find("(")])
                    stats["Abilities"]["Bonuses"][section] = int(nonBlank[i + 1][nonBlank[i + 1].find("+"):nonBlank[i + 1].find(")")])
                    stats["Abilities"]["Saves"][section] = stats["Abilities"]["Bonuses"][section]
                elif section == "Senses":
                    visionTypes = ["darkvision", "blindsight", "tremorsense", "truesight"]
                    for vision in visionTypes:
                        if vision in nonBlank[i + 1]:
                            subsection = nonBlank[i + 1][nonBlank[i + 1].find(vision) + 10:]
                            stats["Senses"][vision[0].upper() + vision[1:]] = int(subsection[:subsection.find("ft")].strip())
            #elif not passedActions and not passedSpellCasting:
                #TODO: parse special traits
            #elif passedSpellCasting and not passedActions:
                #TODO: parse spells
            #elif passedActions:
                #TODO: parse actions


        return stats
    else:
        return ""

#print(monsterDict["Aarakocra"])
print(getMonsterInfo("Drow"))