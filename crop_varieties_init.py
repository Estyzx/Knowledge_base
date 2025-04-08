import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# 修改环境变量设置，确保正确指向Django项目的settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowledge_base.settings')
# 如果上述设置不正确，请尝试以下可能的路径之一：
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # 如果settings.py直接在项目根目录
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knowledge_base.settings')  # 小写项目名

django.setup()

from gannan_orange.models import Variety, PlantingTech, Pest, SoilType, Category
from User.models import CustomUser

# 确保有管理员用户用于审核
admin_user, _ = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'phone': '13800000000',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)

if not admin_user.check_password('admin123'):
    admin_user.set_password('admin123')
    admin_user.save()

# 创建作物类别
category_data = [
    {"name": "谷物", "description": "包括小麦、水稻、玉米等谷物类作物"},
    {"name": "经济作物", "description": "包括棉花、甘蔗、油菜等经济类作物"},
    {"name": "蔬菜", "description": "包括各类叶菜、果菜、根菜等蔬菜类作物"},
    {"name": "水果", "description": "包括各类水果作物"},
    {"name": "豆类", "description": "包括大豆、绿豆、黑豆等豆类作物"}
]

categories = {}
for cat in category_data:
    category, created = Category.objects.get_or_create(
        name=cat["name"],
        defaults={"description": cat["description"]}
    )
    categories[cat["name"]] = category

# 确保有一些基本土壤类型
soil_types_data = [
    {
        "name": "壤土",
        "texture": "loamy",
        "ph_range": "6.0-7.5",
        "organic_matter": 3.5,
        "drainage": "good",
        "water_retention": "medium",
        "fertility": "high",
        "nitrogen_content": 0.20,
        "phosphorus_content": 25.00,
        "potassium_content": 180.00,
        "cation_exchange": 20.00,
        "suitable_crops": "小麦、水稻、玉米、大豆、油菜、棉花、蔬菜等多种作物",
        "improvement_methods": "添加有机肥料，保持适当耕作深度，建议每亩施用腐熟农家肥2000-3000千克，并进行深翻耕作20-25厘米",
        "description": "壤土是综合性能最好的土壤，含有适量的砂粒、粘粒和粉粒，粒径分布均匀，团粒结构发达，具有良好的通气性、透水性和保水性，养分含量丰富，微生物活动活跃，适合多种作物生长。春季升温快，适宜早播早种，PH值一般在6.0-7.5之间，属于中性或弱碱性土壤。"
    },
    {
        "name": "砂质土",
        "texture": "sandy",
        "ph_range": "5.5-7.0",
        "organic_matter": 1.5,
        "drainage": "excellent",
        "water_retention": "low",
        "fertility": "low",
        "nitrogen_content": 0.10,
        "phosphorus_content": 15.00,
        "potassium_content": 120.00,
        "cation_exchange": 10.00,
        "suitable_crops": "花生、甘薯、西瓜、葡萄、向日葵、苜蓿、沙葱等耐旱和根系发达作物",
        "improvement_methods": "增加有机质，每亩施用腐熟农家肥3000-4000千克，使用覆盖物减少水分蒸发，种植绿肥作物进行翻耕，添加粘土或壤土改善质地，建立滴灌或微喷灌系统提高灌溉效率",
        "description": "砂质土是以砂粒(粒径0.02-2.0毫米)为主的土壤，砂粒含量通常在70%以上，质地粗糙，孔隙度大，排水性好但保肥保水性能差。这种土壤春季升温快，有利于早熟作物生长，但有机质含量低，养分易流失，抗旱能力差，适合种植根系发达的耐旱作物和需要疏松土壤环境的作物。在管理上需要频繁灌溉和施肥，宜采用少量多次的方式。"
    },
    {
        "name": "粘土",
        "texture": "clay",
        "ph_range": "6.0-7.0",
        "organic_matter": 4.5,
        "drainage": "poor",
        "water_retention": "high",
        "fertility": "high",
        "nitrogen_content": 0.30,
        "phosphorus_content": 30.00,
        "potassium_content": 200.00,
        "cation_exchange": 25.00,
        "suitable_crops": "水稻、莲藕、芡实、慈姑等水生或耐湿作物，以及根系较浅的蔬菜作物",
        "improvement_methods": "深耕改良(25-30厘米)，增加砂质成分改善质地，每亩施用石灰150-200千克调节酸碱度，建设完善的沟渠排水系统，采用高畦栽培技术，种植绿肥作物增加有机质",
        "description": "粘土是以粘粒(粒径<0.002毫米)为主的土壤，粘粒含量通常在30%以上，质地粘重，孔隙度小，通气性差，保水保肥能力强，但透气性和排水性较差。这种土壤养分含量丰富，阳离子交换量大，肥力较高，但春季升温慢，不宜早播。粘土在干燥时坚硬开裂，湿润时黏滞，难以耕作，适耕期短，适合种植水稻等耐湿作物。管理上需重点改善排水和通气条件。"
    },
    {
        "name": "石灰性土",
        "texture": "chalky",
        "ph_range": "7.2-8.5",
        "organic_matter": 2.0,
        "drainage": "good",
        "water_retention": "medium",
        "fertility": "medium",
        "nitrogen_content": 0.15,
        "phosphorus_content": 20.00,
        "potassium_content": 150.00,
        "cation_exchange": 15.00,
        "suitable_crops": "苜蓿、紫花苜蓿、葡萄、樱桃、小麦、高粱、豆类等喜钙作物",
        "improvement_methods": "增加有机质，每亩施用腐熟农家肥2500-3500千克，使用含硫肥料降低土壤pH值，施用螯合态微量元素肥料防止微量元素缺乏，避免过量施用碱性肥料",
        "description": "石灰性土是含有大量碳酸钙(CaCO₃)的土壤，通常pH值在7.2以上，呈碱性反应。这种土壤通气性和排水性较好，但磷、铁、锰、锌等养分易被固定而导致作物缺乏。石灰性土结构稳定，不易板结，适合种植喜钙作物，但需注意微量元素的补充。在管理上，应注意调节pH值和增加有机质含量，避免使用碱性肥料加重碱害。"
    },
    {
        "name": "黑土",
        "texture": "loamy",
        "ph_range": "6.5-7.2",
        "organic_matter": 5.0,
        "drainage": "moderate",
        "water_retention": "high",
        "fertility": "high",
        "nitrogen_content": 0.35,
        "phosphorus_content": 28.00,
        "potassium_content": 190.00,
        "cation_exchange": 30.00,
        "suitable_crops": "玉米、小麦、大豆、马铃薯、甜菜、向日葵等粮食和经济作物",
        "improvement_methods": "合理轮作倒茬，避免连作，保持适宜耕作深度(20-25厘米)，秸秆还田增加有机质，建设防风林带防止风蚀，适当深松破除犁底层",
        "description": "黑土是世界上最肥沃的土壤之一，含有丰富的有机质，呈黑色或深褐色，团粒结构发达，物理性状良好。黑土层深厚，一般为60-100厘米，养分含量高，微生物活性强，保水保肥能力强，适合多种作物生长。我国东北黑土带是重要的商品粮基地，黑土资源十分宝贵，但面临退化问题，需合理保护和利用。"
    }
]

soil_types = []
for soil_data in soil_types_data:
    soil, created = SoilType.objects.update_or_create(
        name=soil_data["name"],
        defaults={
            "texture": soil_data["texture"],
            "ph_range": soil_data["ph_range"],
            "organic_matter": soil_data["organic_matter"],
            "drainage": soil_data["drainage"],
            "water_retention": soil_data["water_retention"],
            "fertility": soil_data["fertility"],
            "nitrogen_content": soil_data["nitrogen_content"],
            "phosphorus_content": soil_data["phosphorus_content"],
            "potassium_content": soil_data["potassium_content"],
            "cation_exchange": soil_data["cation_exchange"],
            "suitable_crops": soil_data["suitable_crops"],
            "improvement_methods": soil_data["improvement_methods"],
            "description": soil_data["description"],
            "review_status": "approved",
            "reviewer": admin_user,
            "review_date": timezone.now()
        }
    )
    soil_types.append(soil)

# 创建一些常见病虫害
pest_data = [
    {
        "name": "小麦条锈病",
        "scientific_name": "Puccinia striiformis",
        "type": "disease",
        "severity": "severe",
        "occurrence_season": "春季",
        "affected_parts": "叶片、茎秆",
        "symptoms": "初期在叶片上产生黄色条纹状小斑点，后期病斑扩大连成条带，表面生有黄褐色粉状物，为夏孢子堆。",
        "life_cycle": "由菌丝体、夏孢子和冬孢子组成生活史。病菌主要以菌丝体在冬小麦、多年生禾本科植物和自生小麦上越冬。",
        "prevention_methods": "种植抗病品种，合理轮作，适期播种，平衡施肥。",
        "chemical_control": "可使用三唑类杀菌剂如戊唑醇、丙环唑等进行防治。",
        "biological_control": "使用拮抗微生物如木霉菌等。",
        "physical_control": "及时清除田间病株和杂草。",
        "description": "小麦条锈病是世界性的主要小麦病害之一，在中国小麦主产区均有发生，可造成严重减产。"
    },
    {
        "name": "水稻稻瘟病",
        "scientific_name": "Magnaporthe oryzae",
        "type": "disease",
        "severity": "severe",
        "occurrence_season": "夏季",
        "affected_parts": "叶片、穗颈、节间",
        "symptoms": "叶瘟表现为水渍状褐斑，逐渐扩大成纺锤形病斑；穗颈瘟导致穗颈部变褐、枯死，造成秕谷。",
        "life_cycle": "病原菌主要以菌丝体或分生孢子在病残体和稻种上越冬，第二年随风雨传播。",
        "prevention_methods": "种植抗病品种，合理施肥，避免过量施用氮肥，加强水分管理。",
        "chemical_control": "可使用三环唑、稻瘟灵等杀菌剂防治。",
        "biological_control": "使用枯草芽孢杆菌等生物制剂。",
        "physical_control": "收获后彻底清除病残体。",
        "description": "稻瘟病是世界范围内最具破坏性的水稻病害之一，发生严重时可导致20-30%的减产。"
    },
    {
        "name": "棉花枯萎病",
        "scientific_name": "Verticillium dahliae",
        "type": "disease",
        "severity": "severe",
        "occurrence_season": "夏季至秋季",
        "affected_parts": "根系、茎部、叶片",
        "symptoms": "初期下部叶片边缘发黄，后逐渐向内部扩展，形成V字形黄化；严重时全株萎蔫，茎部维管束变褐。",
        "life_cycle": "病原菌以微菌核形式在土壤或病残体中越冬，通过伤口侵染根系，在维管束中生长繁殖。",
        "prevention_methods": "种植抗病品种，实行轮作，避免连作，增施有机肥，使用健康种子。",
        "chemical_control": "可使用咪鲜胺、苯醚甲环唑等进行根部处理。",
        "biological_control": "使用拮抗菌如木霉菌、放线菌等。",
        "physical_control": "及时清除病株，深翻土壤。",
        "description": "棉花枯萎病是棉花生产中最具毁灭性的土传病害之一，一旦发生难以根除，可造成10-30%的减产。"
    }
]

pests = []
for pest_info in pest_data:
    pest, created = Pest.objects.update_or_create(
        name=pest_info["name"],
        defaults={
            "scientific_name": pest_info["scientific_name"],
            "type": pest_info["type"],
            "severity": pest_info["severity"],
            "occurrence_season": pest_info["occurrence_season"],
            "affected_parts": pest_info["affected_parts"],
            "symptoms": pest_info["symptoms"],
            "life_cycle": pest_info["life_cycle"],
            "prevention_methods": pest_info["prevention_methods"],
            "chemical_control": pest_info["chemical_control"],
            "biological_control": pest_info["biological_control"],
            "physical_control": pest_info["physical_control"],
            "description": pest_info["description"],
            "review_status": "approved",
            "reviewer": admin_user,
            "review_date": timezone.now()
        }
    )
    pests.append(pest)

# 创建一些基本种植技术
tech_data = [
    {
        "name": "小麦精量播种技术",
        "category": "planting",
        "difficulty": "intermediate",
        "applicable_season": "autumn",
        "estimated_cost": "中",
        "labor_intensity": "medium",
        "equipment_needed": "精量播种机、拖拉机、播前整地机械",
        "expected_outcome": "提高种子利用率，减少用种量，保证播种质量，提高产量10-15%",
        "description": "小麦精量播种是指通过专用播种机械，按照合理的密度和均匀度将种子播入土壤的播种方式，实现种子在播种带上均匀分布，每颗种子都能获得足够的生长空间。",
        "precautions": "播种前确保土壤墒情适宜，播种深度应控制在3-5厘米，播后适当镇压。"
    },
    {
        "name": "水稻机械化插秧技术",
        "category": "planting",
        "difficulty": "intermediate",
        "applicable_season": "spring",
        "estimated_cost": "中高",
        "labor_intensity": "medium",
        "equipment_needed": "插秧机、秧盘、育秧盘播种机",
        "expected_outcome": "减少劳动力投入80%以上，提高作业效率，确保秧苗整齐度，提高产量5-10%",
        "description": "水稻机械化插秧技术是使用机械设备代替人工进行水稻插秧的技术，包括育秧和插秧两个环节。该技术可大幅降低劳动强度，提高作业效率。",
        "precautions": "插秧前确保田块整平，秧苗质量要好，机械操作要熟练，插深要适宜。"
    },
    {
        "name": "棉花滴灌技术",
        "category": "irrigation",
        "difficulty": "advanced",
        "applicable_season": "summer",
        "estimated_cost": "高",
        "labor_intensity": "low",
        "equipment_needed": "滴灌带、过滤器、施肥罐、水泵",
        "expected_outcome": "节水50%以上，增产15-20%，节省劳动力，可同时进行水肥一体化管理",
        "description": "棉花滴灌技术是通过安装在地面或地下的滴灌管道和滴头，将水分和养分直接输送到棉花根部的灌溉方式，实现精准灌溉和施肥。",
        "precautions": "定期检查滴灌系统是否堵塞，调整好灌溉频次和水量，避免过度灌溉。"
    }
]

planting_techs = []
for tech_info in tech_data:
    tech, created = PlantingTech.objects.update_or_create(
        name=tech_info["name"],
        defaults={
            "category": tech_info["category"],
            "difficulty": tech_info["difficulty"],
            "applicable_season": tech_info["applicable_season"],
            "estimated_cost": tech_info["estimated_cost"],
            "labor_intensity": tech_info["labor_intensity"],
            "equipment_needed": tech_info["equipment_needed"],
            "expected_outcome": tech_info["expected_outcome"],
            "description": tech_info["description"],
            "precautions": tech_info["precautions"],
            "review_status": "approved",
            "reviewer": admin_user,
            "review_date": timezone.now()
        }
    )
    planting_techs.append(tech)

# 创建15种不同作物品种
varieties_data = [
    # 小麦品种
    {
        "name": "京麦9号",
        "scientific_name": "Triticum aestivum L.",
        "origin": "中国北京",
        "maturity_type": "mid",
        "category": categories["谷物"],
        "harvest_season": "6月初至6月中旬",
        "growth_cycle": 240,
        "chill_requirement": 800,
        "altitude_range": "0-800米",
        "tree_shape": "直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "金黄色",
        "fruit_weight": 40.0,
        "brix": 0.0,
        "peel_thickness": 0.2,
        "seed_count": 45,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 450.0,
        "cold_tolerance": "high",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土", "砂质土", "黑土"],
        "description": (
            "京麦9号是由中国农业科学院作物科学研究所选育的半冬性强筋小麦品种，2007年通过国家品种审定。"
            "植株株高85厘米左右，抗倒伏，抗寒性强，抗旱性中等，抗条锈病、白粉病，中抗叶锈病。"
            "籽粒千粒重约40克，容重每升805克，蛋白质含量15.2%，湿面筋32.0%，稳定时间15.5分钟，"
            "拉伸面积118平方厘米，吸水率62.4%，产量高，品质优，适宜制作面包和面条。"
            "适宜华北及黄淮冬麦区播种，推荐播期为10月上中旬，适宜播种量为每亩15-18公斤。"
        ),
        "pests": ["小麦条锈病"],
        "tech": ["小麦精量播种技术"]
    },
    {
        "name": "郑麦366",
        "scientific_name": "Triticum aestivum L.",
        "origin": "中国河南",
        "maturity_type": "mid",
        "category": categories["谷物"],
        "harvest_season": "5月下旬至6月上旬",
        "growth_cycle": 220,
        "chill_requirement": 750,
        "altitude_range": "0-600米",
        "tree_shape": "半直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "金黄色",
        "fruit_weight": 42.0,
        "brix": 0.0,
        "peel_thickness": 0.2,
        "seed_count": 42,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 480.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "high",
        "disease_resistance": "medium",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "黑土"],
        "description": "郑麦366是由河南省农业科学院小麦研究所选育的半冬性中强筋小麦品种，2004年通过国家品种审定。株高88厘米左右，株型较紧凑，抗倒能力强，生长势旺盛。抗旱性好，抗条锈病、中抗叶锈病和白粉病。籽粒千粒重42克左右，容重每升795克，蛋白质含量14.0%，湿面筋30.5%，稳定时间8.2分钟，产量高，适应性广，稳产性好。适宜黄淮冬麦区和北部冬麦区种植，适宜播期为10月上中旬，适宜播种量为每亩12-15公斤，建议亩施纯氮13-15公斤，五氧化二磷6-8公斤，氧化钾6-8公斤。中后期注意防控赤霉病。",
        "pests": ["小麦条锈病"],
        "tech": ["小麦精量播种技术"]
    },
    {
        "name": "济麦22",
        "scientific_name": "Triticum aestivum L.",
        "origin": "中国山东",
        "maturity_type": "early",
        "category": categories["谷物"],
        "harvest_season": "5月中旬至5月下旬",
        "growth_cycle": 210,
        "chill_requirement": 720,
        "altitude_range": "0-500米",
        "tree_shape": "半披散型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "淡黄色",
        "fruit_weight": 38.0,
        "brix": 0.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "砂质土"],
        "description": "济麦22是一种半冬性中筋小麦品种，早熟高产，抗寒性中等，抗旱中等，抗条锈病、叶锈病能力强，适合华北、黄淮麦区种植。",
        "pests": ["小麦条锈病"],
        "tech": ["小麦精量播种技术"]
    },
    
    # 水稻品种
    {
        "name": "黄华占",
        "scientific_name": "Oryza sativa L.",
        "origin": "中国福建",
        "maturity_type": "early",
        "category": categories["谷物"],
        "harvest_season": "10月初至10月中旬",
        "growth_cycle": 120,
        "chill_requirement": 0,
        "altitude_range": "0-500米",
        "tree_shape": "直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "黄色",
        "fruit_weight": 25.0,
        "brix": 0.0,
        "peel_thickness": 0.1,
        "seed_count": 1,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 550.0,
        "cold_tolerance": "low",
        "drought_tolerance": "low",
        "disease_resistance": "medium",
        "waterlogging_tolerance": "high",
        "soil_types": ["粘土"],
        "description": "黄华占是福建省农业科学院水稻研究所育成的一种优质中粳稻品种，通过福建省品种审定。属早熟类型，全生育期120天左右。株高100厘米左右，株型紧凑，分蘖力强，每穗粒数约115粒，结实率85%以上，千粒重25克。米质优良，直链淀粉含量17%左右，胶稠度70毫米，食味佳，适口性好。抗倒伏性好，抗稻瘟病中等，抗白叶枯病、纹枯病能力较强。适应性广，在南方双季稻区表现良好，尤其适合福建等南方稻区作双季早稻或单季稻种植。建议早稻季节3月下旬至4月上旬播种，每亩用种量1.5-2.0公斤，采用30×13厘米的密度插秧，亩插2.5-3万穴。",
        "pests": ["水稻稻瘟病"],
        "tech": ["水稻机械化插秧技术"]
    },
    {
        "name": "南粳46",
        "scientific_name": "Oryza sativa L.",
        "origin": "中国江苏",
        "maturity_type": "mid",
        "category": categories["谷物"],
        "harvest_season": "10月中旬至10月下旬",
        "growth_cycle": 150,
        "chill_requirement": 0,
        "altitude_range": "0-400米",
        "tree_shape": "半直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "淡黄色",
        "fruit_weight": 28.0,
        "brix": 0.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "low",
        "disease_resistance": "high",
        "waterlogging_tolerance": "high",
        "soil_types": ["粘土", "壤土"],
        "description": "南粳46是一种中熟粳稻品种，株型适中，抗病性好，对稻瘟病、白叶枯病有较强抗性，米质优，适合机械化种植，适宜长江中下游稻区种植。",
        "pests": ["水稻稻瘟病"],
        "tech": ["水稻机械化插秧技术"]
    },
    {
        "name": "汕优63",
        "scientific_name": "Oryza sativa L.",
        "origin": "中国广东",
        "maturity_type": "mid",
        "category": categories["谷物"],
        "harvest_season": "10月中旬至11月初",
        "growth_cycle": 140,
        "chill_requirement": 0,
        "altitude_range": "0-600米",
        "tree_shape": "半直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "金黄色",
        "fruit_weight": 27.0,
        "brix": 0.0,
        "cold_tolerance": "low",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "high",
        "soil_types": ["粘土"],
        "description": "汕优63是一种杂交水稻品种，高产稳产，抗病性好，对稻瘟病、白叶枯病、纹枯病均有较好抗性，米质较好，适宜南方稻区种植。",
        "pests": ["水稻稻瘟病"],
        "tech": ["水稻机械化插秧技术"]
    },
    
    # 棉花品种
    {
        "name": "中棉所12号",
        "scientific_name": "Gossypium hirsutum L.",
        "origin": "中国",
        "maturity_type": "mid",
        "category": categories["经济作物"],
        "harvest_season": "9月中旬至10月中旬",
        "growth_cycle": 180,
        "chill_requirement": 0,
        "altitude_range": "0-800米",
        "tree_shape": "塔形",
        "pollination_type": "虫媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "绿色转褐色",
        "fruit_weight": 6.0,
        "brix": 0.0,
        "peel_thickness": 0.8,
        "seed_count": 32,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 0,
        "annual_yield": 350.0,
        "cold_tolerance": "low",
        "drought_tolerance": "high",
        "disease_resistance": "medium",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土", "砂质土"],
        "description": "中棉所12号是中国棉花研究所育成的陆地棉品种，2005年通过国家品种审定。属中熟常规品种，全生育期生长天数北方棉区约为110-120天，长江流域约为130-140天。株高100-120厘米，塔形株型，铃形椭圆，单铃重6.0克，铃数中等，吐絮良好，霜前花铃成熟率高。纤维品质优良，平均长度30.8毫米，马克隆值4.4，比强度32.5厘牛/特克斯，断裂伸长率6.5%，整齐度85%，反射率74%，黄度8.4。对枯萎病和黄萎病抗性中等。适合黄河流域及长江流域棉区种植。建议种植密度每亩1.8-2.2万株，需注意田间水分管理，干旱时及时灌溉，雨季注意排水防涝。",
        "pests": ["棉花枯萎病"],
        "tech": ["棉花滴灌技术"]
    },
    {
        "name": "新陆早28号",
        "scientific_name": "Gossypium hirsutum L.",
        "origin": "中国新疆",
        "maturity_type": "early",
        "category": categories["经济作物"],
        "harvest_season": "9月初至9月底",
        "growth_cycle": 160,
        "chill_requirement": 0,
        "altitude_range": "500-1200米",
        "tree_shape": "紧凑型",
        "pollination_type": "虫媒授粉",
        "fruit_shape": "round",
        "fruit_color": "绿色转褐色",
        "fruit_weight": 5.5,
        "brix": 0.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "high",
        "disease_resistance": "high",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土"],
        "description": "新陆早28号是一种早熟棉花品种，生育期短，结铃集中，吐絮快，纤维品质好，抗病性强，适合新疆及西北地区种植。",
        "pests": ["棉花枯萎病"],
        "tech": ["棉花滴灌技术"]
    },
    {
        "name": "中棉所41",
        "scientific_name": "Gossypium hirsutum L.",
        "origin": "中国",
        "maturity_type": "mid",
        "category": categories["经济作物"],
        "harvest_season": "9月中旬至10月下旬",
        "growth_cycle": 185,
        "chill_requirement": 0,
        "altitude_range": "0-700米",
        "tree_shape": "半开张型",
        "pollination_type": "虫媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "绿色转褐色",
        "fruit_weight": 6.2,
        "brix": 0.0,
        "cold_tolerance": "low",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土", "砂质土"],
        "description": "中棉所41是一种抗虫棉品种，含有Bt基因，对棉铃虫有较强抗性，生长势强，纤维品质优良，抗病性好，适合长江流域及黄河流域棉区种植。",
        "pests": ["棉花枯萎病"],
        "tech": ["棉花滴灌技术"]
    },
    
    # 大豆品种
    {
        "name": "中黄13",
        "scientific_name": "Glycine max (L.) Merr.",
        "origin": "中国",
        "maturity_type": "mid",
        "category": categories["豆类"],
        "harvest_season": "9月下旬至10月上旬",
        "growth_cycle": 130,
        "chill_requirement": 0,
        "altitude_range": "0-800米",
        "tree_shape": "半直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "黄色",
        "fruit_weight": 18.0,
        "brix": 0.0,
        "peel_thickness": 0.3,
        "seed_count": 2,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 250.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土", "黑土"],
        "description": "中黄13是中国农业科学院作物科学研究所选育的中熟大豆品种，2008年通过国家品种审定。全生育期130天左右，属于夏大豆中熟品种。株高75厘米左右，株型紧凑，有限结荚习性，主茎11-13节，分枝2-3个。植株抗倒伏性好，抗病性强，特别是对大豆花叶病毒病和大豆胞囊线虫病抗性表现良好。籽粒椭圆形，种皮黄色，脐色浅褐，子叶黄色，百粒重约18克，蛋白质含量42.0%，含油量22.0%。适合黄淮海地区作夏大豆种植，适宜播期为6月上中旬，建议行距40-50厘米，株距10厘米，每亩种植1.5-1.8万株。亩产可达180-230公斤，高产田块可达250公斤以上。",
        "pests": [],
        "tech": []
    },
    {
        "name": "晋豆23",
        "scientific_name": "Glycine max (L.) Merr.",
        "origin": "中国山西",
        "maturity_type": "early",
        "category": categories["豆类"],
        "harvest_season": "9月中旬",
        "growth_cycle": 115,
        "chill_requirement": 0,
        "altitude_range": "500-1200米",
        "tree_shape": "直立型",
        "pollination_type": "自花授粉",
        "fruit_shape": "oval",
        "fruit_color": "黄色",
        "fruit_weight": 16.0,
        "brix": 0.0,
        "cold_tolerance": "high",
        "drought_tolerance": "high",
        "disease_resistance": "medium",
        "waterlogging_tolerance": "low",
        "soil_types": ["壤土", "砂质土"],
        "description": "晋豆23是一种早熟大豆品种，生育期短，适应性强，耐旱抗寒，籽粒品质良好，蛋白质含量高，适合北方春播区域种植。",
        "pests": [],
        "tech": []
    },
    
    # 玉米品种
    {
        "name": "郑单958",
        "scientific_name": "Zea mays L.",
        "origin": "中国河南",
        "maturity_type": "mid",
        "category": categories["谷物"],
        "harvest_season": "9月初至9月下旬",
        "growth_cycle": 115,
        "chill_requirement": 0,
        "altitude_range": "0-1000米",
        "tree_shape": "直立型",
        "pollination_type": "风媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "黄色",
        "fruit_weight": 320.0,
        "brix": 6.0,
        "peel_thickness": 0.5,
        "seed_count": 580,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 650.0,
        "cold_tolerance": "medium",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "黑土"],
        "description": "郑单958是河南省农业科学院粮食作物研究所与河南农业大学合作选育的中熟玉米杂交种，1996年通过国家品种审定。生育期北方春玉米区为105-115天，黄淮海夏玉米区为95-105天。植株株高260-280厘米，穗位90-110厘米，株型紧凑，茎秆粗壮，抗倒伏能力强。叶片数18-20片，叶鞘紫色，花丝紫色。穗长18-22厘米，穗行数16-18行，穗轴红色，籽粒黄色，半马齿型，千粒重约320克，容重每升750克。抗大斑病、小斑病、茎腐病、丝黑穗病，耐瘠薄，适应性广，稳产性好。适合华北、黄淮海地区种植。春播建议4月上中旬播种，夏播建议6月中旬播种，每亩种植3500-4000株。",
        "pests": [],
        "tech": []
    },
    {
        "name": "先玉335",
        "scientific_name": "Zea mays L.",
        "origin": "中国",
        "maturity_type": "early",
        "category": categories["谷物"],
        "harvest_season": "8月下旬至9月中旬",
        "growth_cycle": 105,
        "chill_requirement": 0,
        "altitude_range": "0-1200米",
        "tree_shape": "半直立型",
        "pollination_type": "风媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "黄色",
        "fruit_weight": 300.0,
        "brix": 0.0,
        "cold_tolerance": "high",
        "drought_tolerance": "high",
        "disease_resistance": "high",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "砂质土"],
        "description": "先玉335是一种早熟玉米杂交种，适应性广，抗逆性强，耐密植，产量高稳，籽粒品质优良，适合北方春玉米区及南方高海拔地区种植。",
        "pests": [],
        "tech": []
    },
    
    # 油菜品种
    {
        "name": "华油杂62",
        "scientific_name": "Brassica napus L.",
        "origin": "中国湖北",
        "maturity_type": "mid",
        "category": categories["经济作物"],
        "harvest_season": "5月上旬至5月中旬",
        "growth_cycle": 240,
        "chill_requirement": 600,
        "altitude_range": "0-800米",
        "tree_shape": "半直立型",
        "pollination_type": "虫媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "褐色",
        "fruit_weight": 4.0,
        "brix": 0.0,
        "peel_thickness": 0.1,
        "seed_count": 18,
        "juice_content": 0.0,
        "acidity": 0.00,
        "sugar_acid_ratio": 0.00,
        "shelf_life": 365,
        "annual_yield": 200.0,
        "cold_tolerance": "high",
        "drought_tolerance": "medium",
        "disease_resistance": "high",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "石灰性土"],
        "description": (
            "华油杂62是华中农业大学选育的中熟双低油菜杂交种，2006年通过国家品种审定。属中熟品种，全生育期约240天。"
            "株高165-175厘米，分枝较多，一次分枝8-10个，总角果数360-390个，每角粒数18-22粒，千粒重4.0克。"
            "抗寒性强，耐旱抗倒性好，抗病性好，对菌核病和霜霉病有较好抗性。平均含油量43.5%，芥酸含量低于1%，"
            "硫苷含量低于25微摩尔/克，是优质的'双低'油菜品种。适合长江流域油菜区及黄淮地区种植。"
            "推荐9月中下旬播种，亩播种量150-200克，幼苗期亩施复合肥15-20公斤，越冬前亩施尿素7-10公斤，"
            "苔期亩施尿素10公斤。亩产可达180-220公斤。"
        ),
        "pests": [],
        "tech": []
    },
    {
        "name": "甘蓝型油菜",
        "scientific_name": "Brassica napus L.",
        "origin": "中国",
        "maturity_type": "late",
        "category": categories["经济作物"],
        "harvest_season": "5月中旬至5月下旬",
        "growth_cycle": 260,
        "chill_requirement": 650,
        "altitude_range": "0-1000米",
        "tree_shape": "开张型",
        "pollination_type": "虫媒授粉",
        "fruit_shape": "oval",
        "fruit_color": "褐色",
        "fruit_weight": 4.2,
        "brix": 0.0,
        "cold_tolerance": "high",
        "drought_tolerance": "medium",
        "disease_resistance": "medium",
        "waterlogging_tolerance": "medium",
        "soil_types": ["壤土", "粘土"],
        "description": "甘蓝型油菜是我国主要种植的油菜类型，适应性广，抗寒性强，种子含油量高，是重要的食用油料作物。",
        "pests": [],
        "tech": []
    }
]

# 创建品种数据并关联
print("开始创建品种数据...")
for variety_data in varieties_data:
    # 获取该品种应关联的土壤类型
    soil_type_names = variety_data.pop("soil_types", [])
    soil_type_objs = []
    for soil_name in soil_type_names:
        soil = SoilType.objects.filter(name=soil_name).first()
        if soil:
            soil_type_objs.append(soil)
    
    # 获取病虫害名称
    pest_names = variety_data.pop("pests", [])
    pest_objs = []
    for pest_name in pest_names:
        pest = Pest.objects.filter(name=pest_name).first()
        if pest:
            pest_objs.append(pest)
    
    # 获取种植技术名称
    tech_names = variety_data.pop("tech", [])
    tech_objs = []
    for tech_name in tech_names:
        tech = PlantingTech.objects.filter(name=tech_name).first()
        if tech:
            tech_objs.append(tech)
    
    # 创建品种
    variety, created = Variety.objects.update_or_create(
        name=variety_data["name"],
        defaults={
            **variety_data,
            "review_status": "approved",
            "reviewer": admin_user,
            "review_date": timezone.now()
        }
    )
    
    # 关联土壤类型
    if soil_type_objs:
        variety.soil_preference.set(soil_type_objs)
    
    # 关联病虫害
    if pest_objs:
        variety.pest.set(pest_objs)
    
    # 关联种植技术
    if tech_objs:
        variety.planting_tech.set(tech_objs)
    
    print(f"已创建品种: {variety.name}")

print("品种数据初始化完成!")
