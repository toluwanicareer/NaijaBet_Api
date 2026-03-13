
from enum import Enum
from pprint import pprint


endpoints = {
    "bet9ja": {
        "sports": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetSports?DISP=0&v_cache_version=1.164.0.135",
        "leaguetry": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEventsInCouponV2?SCHID=492&DISP=0&MKEY=1&v_cache_version=1.169.1.135",
        "leagues": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEventsInGroupV2?GROUPID={leagueid}&DISP=0&GROUPMARKETID=1&matches=true",  # noqa: E501
        "corners": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEventsInGroupV2?GROUPID={leagueid}&DISP=0&GROUPMARKETID=216&matches=true",  # noqa: E501
        "asian_handicap": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEventsInGroupV2?GROUPID={leagueid}&DISP=0&GROUPMARKETID=S_AH&matches=true",  # noqa: E501
        "live": "https://sports.bet9ja.com/desktop/feapi/PalimpsestLiveAjax/GetLiveEventsV3?v_cache_version=1.164.0.135",  # noqa: E501
        "markets": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetGroupMarketsById?GROUPID=170880",
        "matches": "https://sports.bet9ja.com/desktop/feapi/PalimpsestAjax/GetEvent?EVENTID=137750929&v_cache_version=1.164.0.135",  # noqa: E501
    },
    "betking": {
        "popular": "https://sportsapicdn-desktop.betking.com/api/feeds/prematch/mostpopularsports/en/1/5/15/",
        "leagues": "https://sportsapicdn-desktop.betking.com/api/feeds/prematch/en/4/{leagueid}/0/0"
    },
    "nairabet": {
        "leagues": "https://sports-api.nairabet.com/v2/events?country=NG&locale=en&group=g3&platform=desktop&sportId=SOCCER&competitionId={leagueid}&limit=10",
        "leaguesDNB": "https://sports-api.nairabet.com/v2/events?country=NG&locale=en&group=g3&platform=desktop&sportId=SOCCER&competitionId={leagueid}&marketId=DNB&limit=10"
    },
    "sportybet": {
        "leagues": [{"sportId":"sr:sport:1","marketId":"1,18,10,29,11,26,36,14","tournamentId":[[{"sr:tournament:1"}]]}]  # noqa: E231, E501
    },
    "altenar": {
        "leagues": "https://sb2frontend-altenar2.biahosted.com/api/widget/GetEventsByChamp?culture=en-GB&timezoneOffset=-60&integration={integration}&deviceType=1&numFormat=en-GB&countryCode=NG&champId=0&champIds={leagueid}"  # noqa: E501
    },
    "twentytwobet": {
        "leagues": "https://22bet.ng/service-api/LineFeed/Get1x2_VZip?sports=1&champs={leagueid}&count=50&lng=en&tf=3000000&tz=1&mode=4&country=159"  # noqa: E501
    }

}


class Betid(Enum):
    # Tuple: (bet9ja_id, betking_id, nairabet_id, sportybet_id, altenar_id, twentytwobet_id)
    # Legacy betking/nairabet/sportybet IDs are 0/"" for new entries

    # === England ===
    PREMIERLEAGUE = 170880, 841, "EN_PR", 17, 2936, 88637
    CHAMPIONSHIP = 170881, 863, "EN_CH", 18, 2937, 105759
    LEAGUE_ONE = 995354, 909, "EN_L1", 24, 2947, 13709
    LEAGUE_TWO = 995355, 939, "EN_L2", 25, 2946, 24637
    ENGLAND_FA_CUP = 708732, 0, "", 0, 2935, 108319
    ENGLAND_EFL_CUP = 990749, 0, "", 0, 2972, 119237
    ENGLAND_FA_TROPHY = 1169583, 0, "", 0, 3614, 0
    ENGLAND_NATIONAL_LEAGUE = 1057831, 0, "", 0, 3022, 1256221
    ENGLAND_ISTHMIAN_LEAGUE = 0, 0, "", 0, 2957, 305457
    ENGLAND_WSL = 990587, 0, "", 0, 3476, 0

    # === Germany ===
    BUNDESLIGA = 180923, 1007, "DE_BL", 35, 2950, 96463
    BUNDESLIGA_2 = 180924, 1025, "DE_B2", 44, 2954, 109313
    GERMANY_3_LIGA = 168228, 0, "", 0, 3044, 2579233
    GERMANY_DFB_POKAL = 184976, 0, "", 0, 3112, 119235
    GERMANY_DFB_POKAL_WOMEN = 895163, 0, "", 0, 11282, 126679
    GERMANY_REGIONALLIGA_BAYERN = 1603639, 0, "", 0, 0, 78495
    GERMANY_REGIONALLIGA_NORTH = 2532461, 0, "", 0, 0, 28351
    GERMANY_REGIONALLIGA_NORDOST = 1619773, 0, "", 0, 0, 86681
    GERMANY_REGIONALLIGA_SUDWEST = 1014719, 0, "", 0, 0, 83999
    GERMANY_REGIONALLIGA_WEST = 1010314, 0, "", 0, 0, 86469

    # === Spain ===
    LALIGA = 180928, 1108, "ES_PL", 8, 2941, 127733
    LALIGA_2 = 180929, 0, "", 0, 3111, 0
    SPAIN_SEGUNDA_DIVISION = 0, 0, "", 0, 3049, 27687
    SPAIN_COPA_DEL_REY = 1125043, 0, "", 0, 2973, 119243
    SPAIN_REGIONAL_LEAGUE = 0, 0, "", 0, 46552, 915815

    # === France ===
    LIGUE_1 = 950503, 1104, "FR_L1", 34, 2943, 12821
    LIGUE_2 = 958691, 1179, "FR_L2", 182, 3143, 12829
    FRANCE_NATIONAL = 993924, 0, "", 0, 3671, 1692148
    FRANCE_NATIONAL_2 = 7596515, 0, "", 0, 3734, 1679208
    COUPE_DE_FRANCE = 1248227, 0, "", 0, 3070, 119241
    FRANCE_DIVISION_1_WOMEN = 1016655, 0, "", 0, 3441, 0

    # === Italy ===
    SERIEA = 167856, 3775, "IT_SA", 23, 2942, 110163
    ITALY_SERIE_B = 907202, 0, "", 0, 3079, 7067
    ITALY_SERIE_D = 1048505, 0, "", 0, 41433, 33957
    COPPA_ITALIA = 1042342, 0, "", 0, 3102, 127759
    ITALY_COPPA_ITALIA_WOMEN = 1141928, 0, "", 0, 4855, 0

    # === Netherlands ===
    NETHERLANDS_EREDIVISIE = 1016657, 0, "", 0, 3065, 2018750
    NETHERLANDS_EERSTE_DIVISIE = 992239, 0, "", 0, 3066, 2018747
    NETHERLANDS_EREDIVISIE_WOMEN = 1018039, 0, "", 0, 4385, 2026592

    # === Portugal ===
    PORTUGAL_PRIMEIRA_LIGA = 180967, 0, "", 0, 3152, 118663
    PORTUGAL_SEGUNDA_LIGA = 1025450, 0, "", 0, 3388, 17555
    PORTUGAL_CAMPEONATO = 1041236, 0, "", 0, 3335, 0

    # === Scotland ===
    SCOTLAND_PREMIERSHIP = 941378, 0, "", 0, 3023, 13521
    SCOTLAND_CHAMPIONSHIP = 1075222, 0, "", 0, 2962, 281713
    SCOTLAND_LEAGUE_ONE = 1076436, 0, "", 0, 2964, 281719
    SCOTLAND_LEAGUE_TWO = 1076689, 0, "", 0, 2963, 281717

    # === UEFA Competitions ===
    UEFA_CHAMPIONS_LEAGUE = 1185641, 0, "", 0, 16808, 118587
    UEFA_EUROPA_LEAGUE = 1185689, 0, "", 0, 16809, 118593
    UEFA_CONFERENCE_LEAGUE = 1946188, 0, "", 0, 31608, 2252762
    UEFA_CHAMPIONS_LEAGUE_WOMEN = 1688645, 0, "", 0, 17271, 0
    UEFA_NATIONS_LEAGUE = 0, 0, "", 0, 5098, 0

    # === International Competitions ===
    WORLD_CUP_2026 = 2252278, 0, "", 0, 3146, 2708736
    WC_QUAL_UEFA = 1913043, 0, "", 0, 19414, 2708505
    COPA_LIBERTADORES = 2072918, 0, "", 0, 3709, 142091
    CONCACAF_CHAMPIONS_CUP = 1382725, 0, "", 0, 4626, 49527
    AFC_ASIAN_CUP_WOMEN = 2057483, 0, "", 0, 34649, 1735763
    AFC_CHALLENGE_LEAGUE = 0, 0, "", 0, 48237, 2744049
    CAF_CHAMPIONS_LEAGUE = 0, 0, "", 0, 0, 38317
    CAF_CONFEDERATION_CUP = 0, 0, "", 0, 0, 43163

    # === Belgium ===
    BELGIUM_PRO_LEAGUE = 958370, 0, "", 0, 2965, 28787
    BELGIUM_CHALLENGER_PRO_LEAGUE = 989222, 0, "", 0, 3056, 2896025

    # === Turkey ===
    TURKEY_SUPER_LIG = 180956, 0, "", 0, 2951, 11113
    TURKEY_TFF_1_LIG = 180955, 0, "", 0, 3113, 40017
    TURKEY_TFF_2_LIG = 1041711, 0, "", 0, 3718, 59553

    # === Austria ===
    AUSTRIA_BUNDESLIGA = 0, 0, "", 0, 3094, 26031
    AUSTRIA_2_LIGA = 188632, 0, "", 0, 3093, 0

    # === Switzerland ===
    SWITZERLAND_SUPER_LEAGUE = 899893, 0, "", 0, 3059, 27695
    SWITZERLAND_CHALLENGE_LEAGUE = 914179, 0, "", 0, 3118, 1173855
    SWITZERLAND_PROMOTION_LEAGUE = 1393947, 0, "", 0, 4985, 0

    # === Denmark ===
    DENMARK_SUPERLIGA = 0, 0, "", 0, 3145, 8773
    DENMARK_1ST_DIVISION = 522097, 0, "", 0, 3016, 39969
    DENMARK_2ND_DIVISION = 0, 0, "", 0, 5035, 52591

    # === Norway ===
    NORWAY_ELITESERIEN = 817648, 0, "", 0, 3458, 1793471

    # === Sweden ===
    SWEDEN_ALLSVENSKAN = 0, 0, "", 0, 3537, 212425
    SWEDEN_SVENSKA_CUP = 1348079, 0, "", 0, 3160, 0

    # === Greece ===
    GREECE_SUPER_LEAGUE = 1018979, 0, "", 0, 3046, 8777
    GREECE_SUPER_LEAGUE_2 = 1440018, 0, "", 0, 3052, 2008375

    # === Czech Republic ===
    CZECH_REPUBLIC_LIGA = 187345, 0, "", 0, 3105, 30465

    # === Poland ===
    POLAND_EKSTRAKLASA = 400532, 0, "", 0, 3054, 27731
    POLAND_I_LIGA = 196442, 0, "", 0, 4569, 0
    POLAND_II_LIGA = 198342, 0, "", 0, 4707, 0

    # === Romania ===
    ROMANIA_LIGA_1 = 999946, 0, "", 0, 3164, 11121
    ROMANIA_LIGA_2 = 0, 0, "", 0, 3842, 33251

    # === Croatia ===
    CROATIA_HNL = 180725, 0, "", 0, 3061, 0

    # === Serbia ===
    SERBIA_SUPER_LIGA = 609308, 0, "", 0, 3162, 30035

    # === Hungary ===
    HUNGARY_NB_I = 194328, 0, "", 0, 3062, 30213
    HUNGARY_NB_II = 0, 0, "", 0, 3150, 56283

    # === Slovakia ===
    SLOVAKIA_SUPER_LIGA = 0, 0, "", 0, 3106, 27701
    SLOVAKIA_2_LIGA = 965538, 0, "", 0, 5041, 0

    # === Slovenia ===
    SLOVENIA_PRVA_LIGA = 195832, 0, "", 0, 3161, 0

    # === Bulgaria ===
    BULGARIA_FIRST_LEAGUE = 600906, 0, "", 0, 3163, 0

    # === Cyprus ===
    CYPRUS_FIRST_DIVISION = 988097, 0, "", 0, 3040, 12505

    # === Nordic ===
    ICELAND_LEAGUE_CUP = 1292365, 0, "", 0, 4362, 25689
    FINLAND_VEIKKAUSLIIGA = 0, 0, "", 0, 4593, 0
    FAROE_ISLANDS_1ST_DEILD = 1338070, 0, "", 0, 11103, 0

    # === Baltic ===
    ESTONIA_PREMIUM_LIIGA = 1348873, 0, "", 0, 4153, 0
    ESTONIA_ESILIIGA = 1329525, 0, "", 0, 5059, 228159
    LATVIA_VIRSLIGA = 1349174, 0, "", 0, 4886, 120501
    LITHUANIA_A_LIGA = 1332088, 0, "", 0, 4988, 33371

    # === Eastern Europe ===
    UKRAINE_PREMIER_LEAGUE = 988042, 0, "", 0, 4004, 29949
    RUSSIA_PREMIER_LEAGUE = 192011, 0, "", 0, 0, 225733
    GEORGIA_EROVNULI_LIGA = 923989, 0, "", 0, 4053, 0
    GEORGIA_EROVNULI_LIGA_2 = 946324, 0, "", 0, 4959, 0
    AZERBAIJAN_PREMIER_LEAGUE = 920377, 0, "", 0, 4217, 104553
    MONTENEGRO_CFL = 195831, 0, "", 0, 4624, 0
    BOSNIA_PREMIER_LEAGUE = 0, 0, "", 0, 4625, 108683

    # === Northern Ireland / Ireland / Wales ===
    NORTHERN_IRELAND_PREMIERSHIP = 1078221, 0, "", 0, 2961, 11463
    NORTHERN_IRELAND_CHAMPIONSHIP = 1651919, 0, "", 0, 3817, 310027
    IRELAND_PREMIER_DIVISION = 1345657, 0, "", 0, 3571, 0
    IRELAND_FIRST_DIVISION = 1370426, 0, "", 0, 4208, 0
    WALES_PREMIER_LEAGUE = 0, 0, "", 0, 3078, 13721

    # === South America ===
    ARGENTINA_PRIMERA_DIVISION = 0, 0, "", 0, 3075, 119599
    ARGENTINA_PRIMERA_NACIONAL = 2088590, 0, "", 0, 4257, 2922491
    BRAZIL_SERIE_A = 964311, 0, "", 0, 11318, 1268397
    BRAZIL_SERIE_B = 1500335, 0, "", 0, 11005, 57265
    BRAZIL_COPA_DO_BRASIL = 999704, 0, "", 0, 3973, 120013
    CHILE_PRIMERA_DIVISION = 1004077, 0, "", 0, 3837, 28298
    COLOMBIA_PRIMERA_A = 1021140, 0, "", 0, 3857, 214147
    COLOMBIA_PRIMERA_B = 1036246, 0, "", 0, 4009, 214149
    ECUADOR_LIGA_PRO = 1300552, 0, "", 0, 4564, 0
    PARAGUAY_PRIMERA_DIVISION = 1279442, 0, "", 0, 3522, 55479
    PERU_LIGA_1 = 0, 0, "", 0, 4042, 2892390
    URUGUAY_PRIMERA_DIVISION = 1478060, 0, "", 0, 4632, 52183
    VENEZUELA_PRIMERA_DIVISION = 4446741, 0, "", 0, 4251, 289119

    # === North & Central America ===
    USA_MLS = 1387346, 0, "", 0, 4610, 828065
    USA_NWSL = 1469635, 0, "", 0, 11305, 0
    USA_USL_CHAMPIONSHIP = 1432701, 0, "", 0, 5005, 0
    MEXICO_LIGA_MX = 0, 0, "", 0, 10009, 2306111
    MEXICO_LIGA_MX_WOMEN = 0, 0, "", 0, 17210, 2306113
    MEXICO_LIGA_EXPANSION = 1235075, 0, "", 0, 3103, 2126323
    COSTA_RICA_PRIMERA = 1235632, 0, "", 0, 3516, 28665
    HONDURAS_LIGA_NACIONAL = 1300191, 0, "", 0, 3685, 84603
    GUATEMALA_LIGA_NACIONAL = 1307758, 0, "", 0, 4394, 1794524
    GUATEMALA_PRIMERA_DIVISION = 0, 0, "", 0, 4157, 985923

    # === Africa ===
    NIGERIA_PREMIER_LEAGUE = 1209691, 0, "", 0, 0, 611201
    SOUTH_AFRICA_PREMIERSHIP = 976015, 0, "", 0, 2967, 0
    SOUTH_AFRICA_FIRST_DIVISION = 1163518, 0, "", 0, 3381, 0
    EGYPT_PREMIER_LEAGUE = 973090, 0, "", 0, 2974, 147087
    EGYPT_SECOND_DIVISION = 0, 0, "", 0, 3795, 148597
    ALGERIA_LIGUE_1 = 1153296, 0, "", 0, 2939, 28645
    ETHIOPIA_PREMIER_LEAGUE = 1242251, 0, "", 0, 3060, 590333
    UGANDA_PREMIER_LEAGUE = 1164114, 0, "", 0, 2953, 1156373
    TANZANIA_PREMIER_LEAGUE = 644095, 0, "", 0, 2966, 0
    ZAMBIA_SUPER_LEAGUE = 952135, 0, "", 0, 3085, 327197
    BURUNDI_LIGUE_A = 0, 0, "", 0, 3557, 503043
    ANGOLA_GIRABOLA = 1209855, 0, "", 0, 5366, 351439
    SIERRA_LEONE_PREMIER_LEAGUE = 0, 0, "", 0, 39635, 831037
    SENEGAL_CUP = 2453908, 0, "", 0, 28362, 0

    # === Asia ===
    JAPAN_J_LEAGUE = 8631830, 0, "", 0, 3951, 0
    SOUTH_KOREA_K_LEAGUE_1 = 1313502, 0, "", 0, 4276, 30467
    SOUTH_KOREA_K_LEAGUE_2 = 1313503, 0, "", 0, 0, 33137
    CHINA_SUPER_LEAGUE = 1414963, 0, "", 0, 8622, 58043
    INDIA_SUPER_LEAGUE = 1141249, 0, "", 0, 3063, 1122087
    INDIA_I_LEAGUE = 1228153, 0, "", 0, 3151, 253537
    INDONESIA_LIGA_1 = 1692281, 0, "", 0, 4927, 0
    THAILAND_LEAGUE_1 = 1028443, 0, "", 0, 3992, 0
    VIETNAM_V_LEAGUE = 1239966, 0, "", 0, 3991, 28077
    IRAQ_LEAGUE = 2098671, 0, "", 0, 4623, 0

    # === Middle East ===
    SAUDI_PRO_LEAGUE = 971216, 0, "", 0, 2934, 16819
    SAUDI_DIVISION_1 = 971235, 0, "", 0, 3021, 245547
    UAE_PRO_LEAGUE = 1080423, 0, "", 0, 3098, 0
    QATAR_STARS_LEAGUE = 957944, 0, "", 0, 3159, 0
    BAHRAIN_PREMIER_LEAGUE = 974856, 0, "", 0, 3132, 58655
    JORDAN_LEAGUE = 970002, 0, "", 0, 4725, 0
    SYRIA_PREMIER_LEAGUE = 0, 0, "", 0, 3092, 13741

    # === Australia ===
    AUSTRALIA_A_LEAGUE = 1164367, 0, "", 0, 3032, 2905446
    AUSTRALIA_QUEENSLAND_NPL = 1331280, 0, "", 0, 4449, 0
    AUSTRALIA_VICTORIA_NPL = 1315471, 0, "", 0, 4450, 0
    AUSTRALIA_NSW_NPL = 1315470, 0, "", 0, 4969, 0
    AUSTRALIA_SA_NPL = 1400995, 0, "", 0, 4474, 1027167
    AUSTRALIA_NORTHERN_NSW_NPL = 1375233, 0, "", 0, 17075, 981017

    def __init__(self, bet9ja_id, betking_id, nairabet_id, sportybet_id, altenar_id, twentytwobet_id):
        self.bet9ja_id = bet9ja_id
        self.betking_id = betking_id
        self.nairabet_id = nairabet_id
        self.sportybet_id = sportybet_id
        self.altenar_id = altenar_id
        self.twentytwobet_id = twentytwobet_id

    def to_endpoint(self, betting_site, market_type='leagues'):
        if betting_site == 'bet9ja':
            endpoint_url = endpoints[betting_site][market_type].format(
                leagueid=self.bet9ja_id
            )
        elif betting_site == 'betking':
            endpoint_url = endpoints[betting_site]["leagues"].format(
                leagueid=self.betking_id
            )
        elif betting_site == 'nairabet':
            endpoint_url = endpoints[betting_site]["leagues"].format(
                leagueid=self.nairabet_id
            )
        elif betting_site == 'nairabetDNB':
            endpoint_url = endpoints[betting_site]["leaguesDNB"].format(
                leagueid=self.nairabet_id
            )
        elif betting_site == 'altenar':
            endpoint_url = endpoints["altenar"]["leagues"].format(
                leagueid=self.altenar_id,
                integration="{integration}"
            )
        elif betting_site == 'twentytwobet':
            endpoint_url = endpoints[betting_site]["leagues"].format(
                leagueid=self.twentytwobet_id
            )
        elif betting_site == 'sportybet':
            pprint(endpoints[betting_site]["leagues"])
            payload = endpoints[betting_site]["leagues"]
            payload[0]["tournamentId"][0][0] = "sr:tournament:{0}".format(self.sportybet_id)
            pprint(payload)
            return payload
        return endpoint_url
