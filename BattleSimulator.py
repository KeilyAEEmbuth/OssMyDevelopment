from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import graphviz as graphviz
import os
import json
import random as rd

# 리소스 파일 설정 JSON 파일 열기 및 파싱

json_path = os.path.join("BS_resources", "characterStatus.json")
with open(json_path, "r", encoding="utf-8") as f:
    characterData = json.load(f)

json_path = os.path.join("BS_resources", "enemiesInfo.json")
with open(json_path, "r", encoding="utf-8") as f2:
    enemiesData = json.load(f2)

characterCodes = []
for key in characterData:
    characterCodes.append(key)

characterSkillKeywords = [
    "치명타",
    "그랩",
    "점멸",
    "기절"
]

characterSkillCombat = [
    "물리 공격력 계수",
    "주문력 계수"
]

characterSkillTypes = [
    '직접 공격',
    '자신 버프',
    '상대 디버프'
]

characterStatus = [
    "체력",
    "사용 마나",
    "마나 재생",
    "물리 공격력",
    "주문력",
    "방어력",
    "마법 저항력",
    "공격 속도",
    "사거리",
    "이동 속도"
]

# 사용 객체 정의

class characterSkill:
    def __init__(self, skillName, skillDescription, skillKeywords, skillAttackDetail, skillBuffDetail, skillDebuffDetail):
        self.skillName = skillName
        self.skillDescription = skillDescription
        self.skillKeywords = skillKeywords # 리스트로 받음
        self.skillAttackDetail = skillAttackDetail # characterSkillCombat를 키로 하는 딕셔너리로 받음
        self.skillBuffDetail = skillBuffDetail # characterStatus를 키로 하는 딕셔너리로 받음
        self.skillDebuffDetail = skillDebuffDetail # characterStatus를 키로 하는 딕셔너리로 받음

class characterSet:
    def __init__(self, ownSkill, ownStatus, ownName): # characterSkill 객체, ownStatus
        self.characterStatus = ownStatus # characterStatus를 키로 하는 딕셔너리를 받아 스테이터스 및 정보 수치로 삼음
        self.characterName = ownName
        self.characterSkill = ownSkill # characterSkill 객체를 받음

    def getCharacterSkill(self):
        return self.characterSkill

class battleSystem:
    def __init__(self, character1P, character2P):
        self.character1P = character1P # 나 characterSet 객체를 자료로 받음
        self.character2P = character2P # 상대 characterSet 객체를 자료로 받음
        self.winner = None
        self.loser = None
        self.battleLog = []
        self.nowLog = ""
        self.statistics = {"가한 물리 데미지" : 0,
                           "가한 마법 데미지" : 0,
                           "받은 물리 데미지": 0,
                           "받은 마법 데미지": 0,
                           "이동한 거리" : 0,
                           "스킬 사용 횟수" : 0,
                           "재생한 마나량" : 0}


    def writeBattleLog(self):
        self.battleLog.append(self.nowLog)
        self.nowLog = ""

    def setRealStatus(self, characterSet): # 두 캐릭터 객체 정보를 실제로 전투에 사용할 스테이터스 정보로 변환
        resultStatus = {}
        resultStatus["maxHealth"] = characterSet.characterStatus["health"]
        resultStatus["nowHealth"] = characterSet.characterStatus["health"]
        resultStatus["maxMana"] = characterSet.characterStatus["mana"]
        resultStatus["nowMana"] = 0
        resultStatus["chargeMana"] = characterSet.characterStatus["mana_regeneration"]
        resultStatus["attackDamage"] = characterSet.characterStatus["attack_damage"]
        resultStatus["abilityPower"] = characterSet.characterStatus["ability_power"]
        resultStatus["armor"] = characterSet.characterStatus["armor"]
        resultStatus["magicResistance"] = characterSet.characterStatus["magic_resistance"]
        resultStatus["attackSpeed"] = characterSet.characterStatus["attack_speed"]
        resultStatus["range"] = characterSet.characterStatus["range"]
        resultStatus["movementSpeed"] = characterSet.characterStatus["movement_speed"]
        resultStatus["stunTimeLeft"] = 0

        return resultStatus

    def attackAction(self, casterStatus, targetStatus):
        if targetStatus["armor"] > 0:
            realAttackDamage = casterStatus["attackDamage"] / (1 + targetStatus["armor"] * 0.01)  # 실제 롤의 방어력 적용 데미지 수치 적용
        else:
            realAttackDamage = casterStatus["attackDamage"] * (2 - 1 / (1 + targetStatus["armor"] * 0.01))

        targetStatus["nowHealth"] -= realAttackDamage
        self.nowLog = self.nowLog + "상대에게 {0}만큼의 물리 데미지! ".format(int(realAttackDamage))
        return realAttackDamage

    def castSkill(self, usedSkill, casterStatus, targetStatus, distance):

        skillKeywords = usedSkill.skillKeywords

        # 직접 공격의 경우 모션을 수행, 버프 디버프가 들어가기 전에 발동됨
        if "물리 공격력 계수" in usedSkill.skillAttackDetail:
            totalAttackDamage = casterStatus["attackDamage"] * usedSkill.skillAttackDetail["물리 공격력 계수"] / 100
            totalAbilityDamage = casterStatus["abilityPower"] * usedSkill.skillAttackDetail["주문력 계수"] / 100

            if "치명타" in skillKeywords and rd.random() > 0.8:
                self.nowLog = self.nowLog + "치명타로 발동! "
                totalAttackDamage *= 2.0
                totalAbilityDamage *= 2.0

            if targetStatus["armor"] > 0:
                realAttackDamage = totalAttackDamage / (1 + targetStatus["armor"] * 0.01)  # 실제 롤의 방어력 적용 데미지 수치 적용
            else:
                realAttackDamage = totalAttackDamage * (2 - 1 / (1 + targetStatus["armor"] * 0.01))

            if targetStatus["magicResistance"] > 0:
                realAbilityDamage = totalAbilityDamage / (1 + targetStatus["magicResistance"] * 0.01)
            else:
                realAbilityDamage = totalAbilityDamage * (2 - 1 / (1 + targetStatus["magicResistance"] * 0.01))

            if usedSkill.skillAttackDetail["물리 공격력 계수"] != 0:
                targetStatus["nowHealth"] -= realAttackDamage
                self.nowLog = self.nowLog + "{0}만큼의 물리 데미지! ".format(int(realAttackDamage))

            if usedSkill.skillAttackDetail["주문력 계수"] != 0:
                targetStatus["nowHealth"] -= realAbilityDamage
                self.nowLog = self.nowLog + "{0}만큼의 마법 데미지! ".format(int(realAbilityDamage))

            # 자신 버프의 모션을 수행
        if "체력" in usedSkill.skillBuffDetail.keys():
            incresedHealth = casterStatus["maxHealth"] * usedSkill.skillBuffDetail["체력"] / 100
            casterStatus["maxHealth"] += incresedHealth
            casterStatus["nowHealth"] += incresedHealth
        if "사용 마나" in usedSkill.skillBuffDetail.keys():
            casterStatus["maxMana"] *= 1 - usedSkill.skillBuffDetail["사용 마나"] / 100
        if "마나 재생" in usedSkill.skillBuffDetail.keys():
            casterStatus["chargeMana"] *= 1 + usedSkill.skillBuffDetail["마나 재생"] / 100
        if "물리 공격력" in usedSkill.skillBuffDetail.keys():
            casterStatus["attackDamage"] *= 1 + usedSkill.skillBuffDetail["물리 공격력"] / 100
        if "주문력" in usedSkill.skillBuffDetail.keys():
            casterStatus["abilityPower"] *= 1 + usedSkill.skillBuffDetail["주문력"] / 100
        if "방어력" in usedSkill.skillBuffDetail.keys():
            casterStatus["armor"] *= 1 + usedSkill.skillBuffDetail["방어력"] / 100
        if "마법 저항력" in usedSkill.skillBuffDetail.keys():
            casterStatus["magicResistance"] *= 1 + usedSkill.skillBuffDetail["마법 저항력"] / 100
        if "공격 속도" in usedSkill.skillBuffDetail.keys():
            casterStatus["attackSpeed"] *= 1 + usedSkill.skillBuffDetail["공격 속도"] / 100
        if "사거리" in usedSkill.skillBuffDetail.keys():
            casterStatus["range"] *= 1 + usedSkill.skillBuffDetail["사거리"] / 100
        if "이동 속도" in usedSkill.skillBuffDetail.keys():
            casterStatus["movementSpeed"] *= 1 + usedSkill.skillBuffDetail["이동 속도"] / 100

            # 상대 디버프의 모션을 수행
        if "체력" in usedSkill.skillDebuffDetail.keys():
            decresedHealth = targetStatus["maxHealth"] * usedSkill.skillDebuffDetail["체력"] / 100
            targetStatus["maxHealth"] -= decresedHealth
            if targetStatus["maxHealth"] < targetStatus["nowHealth"]:
                targetStatus["nowHealth"] = targetStatus["maxHealth"]
        if "사용 마나" in usedSkill.skillDebuffDetail.keys():
            targetStatus["maxMana"] *= 1 + usedSkill.skillDebuffDetail["사용 마나"] / 100
        if "마나 재생" in usedSkill.skillDebuffDetail.keys():
            targetStatus["chargeMana"] *= 1 - usedSkill.skillDebuffDetail["마나 재생"] / 100
        if "물리 공격력" in usedSkill.skillDebuffDetail.keys():
            targetStatus["attackDamage"] *= 1 - usedSkill.skillDebuffDetail["물리 공격력"] / 100
        if "주문력" in usedSkill.skillDebuffDetail.keys():
            targetStatus["abilityPower"] *= 1 - usedSkill.skillDebuffDetail["주문력"] / 100
        if "방어력" in usedSkill.skillDebuffDetail.keys():
            targetStatus["armor"] *= 1 - usedSkill.skillDebuffDetail["방어력"] / 100
        if "마법 저항력" in usedSkill.skillDebuffDetail.keys():
            targetStatus["magicResistance"] *= 1 - usedSkill.skillDebuffDetail["마법 저항력"] / 100
        if "공격 속도" in usedSkill.skillDebuffDetail.keys():
            targetStatus["attackSpeed"] *= 1 - usedSkill.skillDebuffDetail["공격 속도"] / 100
        if "사거리" in usedSkill.skillDebuffDetail.keys():
            targetStatus["range"] *= 1 - usedSkill.skillDebuffDetail["사거리"] / 100
        if "이동 속도" in usedSkill.skillDebuffDetail.keys():
            targetStatus["movementSpeed"] *= 1 - usedSkill.skillDebuffDetail["이동 속도"] / 100

        # 키워드 액션을 수행
        if "그랩" in skillKeywords:
            distance = 0
        if "점멸" in skillKeywords:
            distance = 800
        if "기절" in skillKeywords:
            targetStatus["stunTimeLeft"] = 1.0

        # 스킬 키워드 사용 여부 표시

        for keyword in skillKeywords:
            self.nowLog = self.nowLog + keyword + "! \n"

        # 값이 바로 바뀌지 않으므로 리턴
        return realAttackDamage, realAbilityDamage

    def runBattle(self):

        Battler1Skill = self.character1P.getCharacterSkill()
        Battler1Status = self.setRealStatus(self.character1P)
        Battler1Delay = 0

        Battler2Skill = self.character2P.getCharacterSkill()
        Battler2Status = self.setRealStatus(self.character2P)
        Battler2Delay = 0
        distance = 1000 # 두 캐릭터간의 거리

        battleActive = True
        timecount = 0.0
        while battleActive:
            # 전투 진행 순서, 캐릭터 둘은 이동, 공격, 스킬 사용 3개중 하나를 행동 원리에 따라 사용할 수 있다.
            # 0순위. Battler1과 Battle2의 모션 사용이 겹칠 시엔 Battler1이 우선 발동한다, 기절 상태에선 아무 액션을 수행할 수 없다.
            # 1순위. 스킬 사용이 가능할 경우 스킬 사용을 한다. 스킬 사용은 nowMana >= maxMana 여야 한다.
            # 2순위. Battler의 Delay가 있을 경우 스킬 사용 외에 모션을 취할 수 없다.
            # 3순위. 평타 공격이 가능할 경우 평타 공격을 한다. 평타 공격은 Battler의 range >= distance이고 Battler의 Delay가 0이어야 한다.
            # 4순위. Battler의 range < distance이고 Delay가 0일 경우 이동하여 상대와의 거리를 좁힌다.

            # 스킬 사용 액션 및 조건

            if Battler1Status["nowMana"] >= Battler1Status["maxMana"] and Battler1Status["stunTimeLeft"] <= 0:
                self.nowLog += self.character1P.characterName + "이(가) 스킬 " + Battler1Skill.skillName + "를 사용! "
                Battler1Status["nowMana"] = 0
                inflictAttackDamage, inflictAbilityDamage = self.castSkill(Battler1Skill, Battler1Status, Battler2Status, distance)
                self.statistics["가한 물리 데미지"] += inflictAttackDamage
                self.statistics["가한 마법 데미지"] += inflictAbilityDamage
                self.statistics["스킬 사용 횟수"] += 1

            if Battler2Status["nowMana"] >= Battler2Status["maxMana"] and Battler2Status["stunTimeLeft"] <= 0:
                self.nowLog += self.character2P.characterName + "이(가) 스킬 " + Battler2Skill.skillName + "를 사용! "
                Battler2Status["nowMana"] = 0
                hitAttackDamage, hitAbilityDamage = self.castSkill(Battler2Skill, Battler2Status, Battler1Status, distance)
                self.statistics["받은 물리 데미지"] += hitAttackDamage
                self.statistics["받은 마법 데미지"] += hitAbilityDamage

            # 평타 사용 액션 및 조건

            if Battler1Delay <= 0 and Battler1Status["range"] >= distance and Battler1Status["stunTimeLeft"] <= 0:
                self.nowLog = self.nowLog + self.character1P.characterName + "이(가) 공격! "
                inflictAttackDamage = self.attackAction(Battler1Status, Battler2Status)
                Battler1Delay = 1 / Battler1Status["attackSpeed"]
                self.statistics["가한 물리 데미지"] += inflictAttackDamage

            if Battler2Delay <= 0 and Battler2Status["range"] >= distance and Battler2Status["stunTimeLeft"] <= 0:
                self.nowLog = self.nowLog + self.character2P.characterName + "이(가) 공격! "
                hitAttackDamage = self.attackAction(Battler2Status, Battler1Status)
                Battler2Delay = 1 / Battler2Status["attackSpeed"]
                self.statistics["받은 물리 데미지"] += hitAttackDamage


            # 이동 액션 사용 및 조건

            if Battler1Delay <= 0 and Battler1Status["range"] < distance and Battler1Status["stunTimeLeft"] <= 0:
                distance -= Battler1Status["movementSpeed"] * 0.1
                self.statistics["이동한 거리"] += Battler1Status["movementSpeed"] * 0.1

            if Battler2Delay <= 0 and Battler2Status["range"] < distance and Battler2Status["stunTimeLeft"] <= 0:
                distance -= Battler2Status["movementSpeed"] * 0.1

            # 마나 재생, 공격 딜레이, 시간 틱에 따른 판정 진행

            timecount += 0.1
            if Battler1Status["stunTimeLeft"] > 0:
                Battler1Status["stunTimeLeft"] -= 0.1
            if Battler2Status["stunTimeLeft"] > 0:
                Battler2Status["stunTimeLeft"] -= 0.1

            Battler1Status["nowMana"] += Battler1Status["chargeMana"] / 10
            self.statistics["재생한 마나량"] += Battler1Status["chargeMana"] / 10
            Battler2Status["nowMana"] += Battler2Status["chargeMana"] / 10
            Battler1Delay -= 0.1
            Battler2Delay -= 0.1

            # 모든 액션이 수행된 뒤 승패 판정을 진행

            if Battler1Status["nowHealth"] <= 0: # 패배 판정도 먼저 진행됨
                battleActive = False
                self.winner = self.character2P
                self.loser = self.character1P
                self.nowLog += self.nowLog + self.character2P.characterName + "의 승리!"
            if Battler2Status["nowHealth"] <= 0:
                battleActive = False
                self.winner = self.character1P
                self.loser = self.character2P
                self.nowLog += self.nowLog + self.character1P.characterName + "의 승리!"
            if timecount > 50: # 50초 안에도 승부가 나지 않을 시 무승부 처리
                battleActive = False
                self.winner = None
                self.loser = None
                self.nowLog += self.nowLog + "승부가 나지 않았다!"

            if self.nowLog != "":
                self.writeBattleLog()

# 사용 함수 정의

def presetChampion(character_preset):
    pass

# 시뮬레이터 소개 및 설명

st.title("⚔️ 임의의 챔피언 배틀 시뮬레이터")
st.markdown("당신만의 챔피언의 이름과 사진, 스테이터스, 스킬셋을 직접 설정하고 적들과 배틀시켜보세요!")
st.subheader("시뮬레이터 사용법")

st.markdown("---")

# 챔피언 1의 사전 설정, 캐릭터 설정도 함께 진행
playerDataset = {}
playerAttackDetail = {}
playerBuffDetail = {}
playerDebuffDetail = {}
playerSkillInfo = {}

st.subheader("챔피언 설정")

col1, col2 = st.columns(2)

with col1:
    uploaded_sprite = st.file_uploader('**캐릭터 이미지 업로드**')
    selected_sprite = st.selectbox('**기존 캐릭터 이미지 선택**', characterData)

    # 이미지 띄우기
    if uploaded_sprite is not None:  # 업로드한 이미지 우선
        new_sprite = Image.open(uploaded_sprite)
        st.image(new_sprite, caption="당신의 캐릭터 이미지(업로드)")
    elif selected_sprite is not None and selected_sprite != "None":  # 프리셋 이미지 차순
        sprite_Path = os.path.join("BS_resources", characterData[selected_sprite]["sprite"])
        st.image(sprite_Path, caption="당신의 캐릭터 이미지(프리셋)")
    else:  # 아무것도 없을 경우 기본 이미지
        st.image("kid.jpg", caption="Image 1")

    # 사용하는 스킬 목록
    playerSkillInfo["skillName"] = st.text_input("**사용 스킬명**")
    playerSkillInfo["skillDescription"] = st.text_area("**사용 스킬 설명**")

    # 스킬 세부사항 결정하는 부분
    st.markdown("##### 스킬 세부 정보")
    skill_type = st.multiselect('스킬 효과', characterSkillTypes)
    selected_actions = st.multiselect('채용 키워드', characterSkillKeywords)
    playerSkillInfo["skillKeywords"] = selected_actions
    st.caption('해당 캐릭터의 스킬의 세부 사항을 정해보세요')

    # 스킬의 타입 및 계수 결정
    for type in skill_type:
        if type == "직접 공격":
            playerAttackDetail["물리 공격력 계수"] = st.number_input("물리 공격 계수 (0 ~ 500 (%))", 0 ,500)
            playerAttackDetail["주문력 계수"] = st.number_input("주문력 계수 (0 ~ 500 (%))", 0, 500)
        if type == "자신 버프":
            st.markdown("버프할 스탯 (0 ~ 30 (%))")
            st.caption("사용 마나 버프는 감소량으로 적용됩니다.")
            for status in characterStatus:
                selectBuff = st.checkbox(status + "+")
                if selectBuff:
                    playerBuffDetail[status] = st.number_input(status, 0, 30)
        if type == "상대 디버프":
            st.markdown("디버프할 스탯 (0 ~ 30 (%))")
            st.caption("사용 마나 디버프는 증가량으로 적용됩니다.")
            for status in characterStatus:
                selectDebuff = st.checkbox(status + "-")
                if selectDebuff:
                    playerDebuffDetail[status] = st.number_input(status, 0, 30)

    # 스킬 키워드 세부사항 결정
    for action in selected_actions:
        if action == "치명타":
            st.info("ℹ️ 치명타 : 20% 확률로 스킬 데미지가 2배로 증가합니다. 버프, 디버프에도 적용됩니다.")
        if action == "그랩":
            st.info("ℹ️ 그랩 : 즉시 바로 서로가 서로를 공격할 수 있는 근접 상태로 만듭니다.")
        if action == "점멸":
            st.info("ℹ️ 점멸 : 즉시 상대와 나의 거리를 800만큼 벌립니다.")
        if action == "기절":
            st.info("ℹ️ 기절 : 상대는 1초 동안 아무 공격 모션을 수행할 수 없습니다.")

with col2:
    playerDataset["name"] = st.text_input('캐릭터 이름')
    playerDataset["health"] = st.slider('체력', 1, 5000)
    playerDataset["mana"] = st.slider('사용 마나', 0, 500)
    playerDataset["mana_regeneration"] = st.slider('마나 재생', 0, 100)
    playerDataset["attack_damage"] = st.slider("물리 공격력", 0, 300)
    playerDataset["ability_power"] = st.slider("주문력", 0, 300)
    playerDataset["armor"] = st.slider("방어력", 0, 200)
    playerDataset["magic_resistance"] = st.slider("마법 저항력", 0, 200)
    playerDataset["attack_speed"] = st.slider("공격 속도", 0.1, 3.0)
    playerDataset["range"] = st.slider("사거리", 100, 1000)
    playerDataset["movement_speed"] = st.slider("이동 속도", 100, 1000)

# 프리셋 사용시 등록되있는 이미지와 스테이터스로 맞춰짐 - 나중에 일단 패스

    PresetChamp1 = st.selectbox('챔피언 1 정보 프리셋', characterCodes)
    st.caption('⚠️ 현재 미구현')
    if PresetChamp1 == 'None':
        pass
    else:
        for element in characterCodes:
            if PresetChamp1 == element:
                presetChampion(characterData[element])
                st.markdown("사전 설정 완료!")

st.markdown("---")
st.subheader("실제 전투 진행")

st.markdown("당신이 만든 캐릭터가 각기 다른 특성을 가진 10단계의 적과 전투합니다. 당신의 캐릭터는 얼마나 강력한 적까지 무찌를 수 있을까요?")
st.markdown("무작정 수치를 높이면 당연히 많이 무찌를 수 있겠지만, 최대한 작은 수치로도 강력한 적을 잡을 수 있는 효율적인 조합과 스텟 분배를 보여주세요!")

# 캐릭터 정보 확정
col1to1, col1to2 = st.columns(2)
with col1to1:
    fixed1P = st.button("캐릭터 정보 확정")
with col1to2:
    fixed2P = st.button("취소")
if fixed1P and not fixed2P:
    st.caption("캐릭터 정보 확정 완료!")
    st.markdown("##### 전투 결과")

    playerSkill = characterSkill(playerSkillInfo["skillName"],
                                 playerSkillInfo["skillDescription"],
                                 playerSkillInfo["skillKeywords"],
                                 playerAttackDetail,
                                 playerBuffDetail,
                                 playerDebuffDetail
                                 )

    PlayerCharacter = characterSet(playerSkill, playerDataset, playerDataset["name"])

    mainBattles = []
    mainCols = []
    totalStatistics = pd.DataFrame(data={"가한 물리 데미지" : [0,0,0,0,0,0,0,0,0,0],
                           "가한 마법 데미지" : [0,0,0,0,0,0,0,0,0,0],
                           "받은 물리 데미지": [0,0,0,0,0,0,0,0,0,0],
                           "받은 마법 데미지": [0,0,0,0,0,0,0,0,0,0],
                           "이동한 거리" : [0,0,0,0,0,0,0,0,0,0],
                           "스킬 사용 횟수" : [0,0,0,0,0,0,0,0,0,0],
                           "재생한 마나량" : [0,0,0,0,0,0,0,0,0,0]})

    count = 0
    for enemy in enemiesData:
        enemySkill = characterSkill(enemy["skillSet"]["skillName"],
                                 enemy["skillSet"]["skillDescription"],
                                 enemy["skillSet"]["skillKeywords"],
                                 enemy["skillSet"]["skillAttackDetail"],
                                 enemy["skillSet"]["skillBuffDetail"],
                                 enemy["skillSet"]["skillDebuffDetail"]
                                 )

        enemyCharacter = characterSet(enemySkill, enemy["dataSet"], enemy["dataSet"]["name"])
        mainBattles.append(battleSystem(PlayerCharacter, enemyCharacter))



    for result in mainBattles:
        result.runBattle()

        # if result.winner.charactername == playerDataset["name"]: # 플레이어가 이겼으면

        st.markdown("## Round " + str(count + 1))
        st.markdown("---")
        screen1P, vs, screen2P = st.columns(3)

        with screen1P:
            if uploaded_sprite is not None:  # 업로드한 이미지 우선
                st.image(new_sprite, caption=playerDataset["name"])
            elif selected_sprite is not None and selected_sprite != "None":  # 프리셋 이미지 차순
                st.image(sprite_Path, caption=playerDataset["name"])
            else:  # 아무것도 없을 경우 기본 이미지
                st.image("kid.jpg", caption=playerDataset["name"])
        with vs:
            st.header("VS")
        with screen2P:
            enemyPath = os.path.join("BS_resources", enemiesData[count]["dataSet"]["sprite"])
            st.image(enemyPath, caption=enemiesData[count]["dataSet"]["name"])

        mainCols.append((screen1P, vs, screen2P))

        for key, value in result.statistics.items():
            totalStatistics.loc[count, key] = value

        for log in result.battleLog:
            st.caption(log)
        count += 1
        st.markdown("---")

    st.subheader("전투 통계")
    st.dataframe(totalStatistics)

    st.bar_chart(totalStatistics.mean(axis=0))