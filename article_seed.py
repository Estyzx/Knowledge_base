import os
import django
import random
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Knowledge_base.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from article.models import Category, Tag, PlantingTechArticle
from User.models import CustomUser
from gannan_orange.models import Variety, PlantingTech, Pest, SoilType

def create_sample_articles():
    """创建示例文章"""
    print("开始创建示例文章...")
    
    # 确保有管理员用户
    admin_user, created = CustomUser.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'phone': '13800000000',  # 添加必需的手机号字段
            'role': 'admin'  # 设置正确的角色
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("已创建管理员用户")
    
    # 创建专家用户以便审核
    expert_user, created = CustomUser.objects.get_or_create(
        username='expert',
        defaults={
            'email': 'expert@example.com',
            'is_staff': True,
            'phone': '13900000000',
            'role': 'expert'
        }
    )
    if created:
        expert_user.set_password('expert123')
        
        # 添加审核权限
        content_types = [
            ContentType.objects.get_for_model(Variety),
            ContentType.objects.get_for_model(PlantingTech),
            ContentType.objects.get_for_model(Pest),
            ContentType.objects.get_for_model(SoilType)
        ]
        
        for ct in content_types:
            for action in ['add', 'change', 'delete', 'view']:
                permission = Permission.objects.get(
                    codename=f'{action}_{ct.model}',
                    content_type=ct
                )
                expert_user.user_permissions.add(permission)
        
        expert_user.save()
        print("已创建专家用户，并分配审核权限")
    
    # 创建普通用户用于测试
    farmer_user, created = CustomUser.objects.get_or_create(
        username='farmer',
        defaults={
            'email': 'farmer@example.com',
            'phone': '13700000000',
            'role': 'farmer'
        }
    )
    if created:
        farmer_user.set_password('farmer123')
        farmer_user.save()
        print("已创建普通用户")
    
    # 创建分类
    categories = [
        {
            'name': '种植技术',
            'description': '包含各类作物的栽培管理、种植方法等技术指导'
        },
        {
            'name': '病虫害防治',
            'description': '针对农作物病虫害的识别、预防和治疗方法'
        },
        {
            'name': '土壤管理',
            'description': '土壤改良、肥料使用、水分管理等相关内容'
        },
        {
            'name': '有机种植',
            'description': '不使用化学农药、化肥的有机种植方法和技术'
        },
        {
            'name': '农业科技',
            'description': '现代农业科技应用、智慧农业、农业设备使用等'
        }
    ]
    
    category_objs = []
    for cat in categories:
        cat_obj, created = Category.objects.get_or_create(
            name=cat['name'],
            defaults={'description': cat['description']}
        )
        category_objs.append(cat_obj)
        if created:
            print(f"已创建分类: {cat['name']}")
    
    # 创建标签
    tags = [
        '水稻', '小麦', '玉米', '果树', '蔬菜', '有机栽培', 
        '节水技术', '施肥', '修剪', '病虫害', '防治', '土壤改良',
        '农业机械', '种子处理', '灌溉', '农药使用', '生物防治'
    ]
    
    tag_objs = []
    for tag_name in tags:
        tag_obj, created = Tag.objects.get_or_create(name=tag_name)
        tag_objs.append(tag_obj)
        if created:
            print(f"已创建标签: {tag_name}")
    
    # 文章内容
    articles = [
        {
            'title': '水稻旱育秧插技术详解',
            'content': """
<h2>水稻旱育秧插技术的基本原理和操作方法</h2>

<p>水稻旱育秧是一种节水、省工、高效的水稻育秧技术，适合在水资源短缺地区推广使用。与传统水育秧相比，具有用水量少、秧苗素质好、适应性强等优点。</p>

<h3>一、旱育秧的基本原理</h3>

<p>旱育秧是在不积水的条件下进行育秧，只保持土壤湿润，使种子在有氧条件下发芽生长，形成根系发达、抗逆性强的壮秧。</p>

<h3>二、旱育秧的操作步骤</h3>

<h4>1. 种子处理</h4>
<ul>
    <li>选用纯度高、发芽率在95%以上的优质种子</li>
    <li>用55-60℃温水浸种20分钟进行消毒</li>
    <li>用清水浸种24-48小时，至胚芽露白</li>
    <li>捞出后用湿布或湿麻袋覆盖，保持30℃左右催芽至芽长1-2毫米</li>
</ul>

<h4>2. 秧床准备</h4>
<ul>
    <li>选择背风向阳、地势平坦、排水良好的地块作秧田</li>
    <li>深翻耕细作，每亩施腐熟有机肥1000-1500公斤，过磷酸钙25公斤</li>
    <li>整平做畦，畦宽1.2-1.5米，高度10-15厘米，畦与畦之间留30厘米的沟</li>
</ul>

<h4>3. 播种方法</h4>
<ul>
    <li>每亩秧田播种量7-8公斤，每平方米播种量50-60克</li>
    <li>均匀撒播后轻轻耙平，盖土厚度1-1.5厘米</li>
    <li>播后覆盖地膜或草苫保温保湿</li>
</ul>

<h4>4. 秧苗管理</h4>
<ul>
    <li>出苗前保持秧床湿润，温度控制在25-30℃</li>
    <li>当80%以上的秧苗出土后，揭除覆盖物</li>
    <li>秧苗期间保持"湿而不干、干而不旱"的水分状态</li>
    <li>2叶1心期追施尿素5公斤/亩</li>
    <li>3叶1心期进行炼苗，控制灌水，增强秧苗抗性</li>
</ul>

<h3>三、旱育秧的优势与注意事项</h3>

<h4>优势：</h4>
<ul>
    <li>节水80-90%，比传统水育秧节约用水量</li>
    <li>秧苗素质好，根系发达，抗逆性强</li>
    <li>秧龄可适当延长，管理灵活性大</li>
    <li>减少了烂秧、僵苗现象，秧苗成活率高</li>
</ul>

<h4>注意事项：</h4>
<ul>
    <li>注意温度管理，避免低温伤害</li>
    <li>控制好水分，保持适度湿润</li>
    <li>注意防治蚜虫、地老虎等虫害</li>
    <li>移栽时带土移栽，减少伤根</li>
</ul>

<h3>四、适用地区</h3>

<p>旱育秧技术适用于我国南方和北方水稻种植区，特别是水资源短缺、劳动力紧张的地区更为适合推广。根据当地气候条件可以灵活调整育秧方式和管理措施。</p>
            """,
            'category': category_objs[0],  # 种植技术
            'tags': [tag_objs[0], tag_objs[6], tag_objs[13]]  # 水稻、节水技术、种子处理
        },
        {
            'title': '小麦条锈病的综合防治技术',
            'content': """
<h2>小麦条锈病的综合防治技术</h2>

<p>小麦条锈病是由禾谷条锈菌引起的一种真菌性病害，是小麦生产中最具毁灭性的病害之一，严重发生时可造成30%-50%的减产，甚至绝收。本文介绍小麦条锈病的识别与综合防治技术。</p>

<h3>一、发病症状与识别</h3>

<p>条锈病主要危害小麦叶片、叶鞘和麦穗。</p>

<ul>
    <li><strong>早期症状</strong>：叶片上出现淡黄色小点，逐渐发展为橙黄色条形或长椭圆形小脓疱，排列成条状</li>
    <li><strong>中期症状</strong>：脓疱破裂后释放出橙黄色粉末状物质（夏孢子），形成明显的黄色条纹</li>
    <li><strong>后期症状</strong>：病部变为褐色至黑色，形成越冬孢子堆</li>
</ul>

<p>与其他锈病区别：条锈病脓疱排列成明显的条纹状，而叶锈病呈散生圆形脓疱，秆锈病脓疱多分布在茎秆上且颜色较深。</p>

<h3>二、发病条件与流行规律</h3>

<ul>
    <li><strong>适宜温度</strong>：11-13℃，相对湿度95%以上时最有利于发病</li>
    <li><strong>传播方式</strong>：主要通过风力传播夏孢子，可长距离扩散</li>
    <li><strong>越冬与初侵染源</strong>：在南方温暖地区可通过冬小麦越冬，次春成为北方小麦区的初侵染源</li>
</ul>

<h3>三、综合防治技术</h3>

<h4>1. 农业防治</h4>

<ul>
    <li><strong>种植抗病品种</strong>：选用高抗或中抗条锈病的小麦品种，如永良4号、邯6172、西农979等</li>
    <li><strong>合理轮作</strong>：实行小麦与非寄主作物轮作，减少病菌积累</li>
    <li><strong>合理密植</strong>：避免过密种植，保持田间通风透光良好</li>
    <li><strong>均衡施肥</strong>：避免偏施氮肥，增施磷钾肥，提高植株抗病性</li>
    <li><strong>清除病源</strong>：及时清除田间自生麦苗和寄主杂草</li>
</ul>

<h4>2. 化学防治</h4>

<ul>
    <li><strong>种子处理</strong>：播前用25%咪鲜胺可湿性粉剂500倍液浸种</li>
    <li><strong>预防性喷药</strong>：在发病初期或流行前，喷施下列药剂之一：</li>
    <ul>
        <li>25%嘧菌酯悬浮剂1500-2000倍液</li>
        <li>40%戊唑醇乳油8000-10000倍液</li>
        <li>15%三唑酮可湿性粉剂1000-1500倍液</li>
        <li>12.5%烯唑醇乳油1500-2000倍液</li>
    </ul>
    <li><strong>治疗性喷药</strong>：发病后7-10天喷一次药，连续2-3次</li>
</ul>

<h4>3. 生物防治</h4>

<ul>
    <li>使用枯草芽孢杆菌等微生物制剂，如5%春雷霉素水剂500倍液</li>
    <li>利用拮抗菌如木霉菌制剂喷施，抑制病菌生长</li>
</ul>

<h4>4. 综合防治策略</h4>

<ul>
    <li><strong>苗期监测</strong>：重点关注田间初侵染情况，发现病株及时铲除</li>
    <li><strong>春季预防</strong>：在返青期进行第一次预防性喷药</li>
    <li><strong>重点时期保护</strong>：在拔节至抽穗期加强防治，这是条锈病流行的高峰期</li>
    <li><strong>建立预警系统</strong>：与气象部门合作，根据气象条件预测发病风险</li>
</ul>

<h3>四、不同区域防治要点</h3>

<ul>
    <li><strong>南方越冬区</strong>：注重秋末冬初的预防，切断初侵染源</li>
    <li><strong>北方春小麦区</strong>：注重早期监测和预防性喷药</li>
    <li><strong>冬麦-春麦过渡区</strong>：加强区域联防联控，防止病害扩散</li>
</ul>

<p>通过合理实施以上综合防治技术，可有效控制小麦条锈病的发生，保障小麦产量和品质。</p>
            """,
            'category': category_objs[1],  # 病虫害防治
            'tags': [tag_objs[1], tag_objs[9], tag_objs[10], tag_objs[16]]  # 小麦、病虫害、防治、生物防治
        },
        {
            'title': '果园土壤酸化改良技术方案',
            'content': """
<h2>果园土壤酸化改良技术方案</h2>

<p>果园土壤酸化是当前我国南方果园普遍存在的问题，长期使用化肥、农药和不合理的水土管理导致土壤pH值降低，影响果树生长和果实品质。本文介绍果园酸化土壤的改良技术方案。</p>

<h3>一、酸化土壤的危害</h3>

<ul>
    <li><strong>养分失衡</strong>：酸化土壤中铝、锰等元素活性增强，产生毒害作用</li>
    <li><strong>养分有效性降低</strong>：磷、钙、镁等养分有效性降低，肥料利用率下降</li>
    <li><strong>有益微生物减少</strong>：土壤微生物区系失调，有益微生物数量减少</li>
    <li><strong>根系生长受阻</strong>：果树根系发育不良，吸收功能下降</li>
    <li><strong>病害加重</strong>：土传病害发生风险增加，如疫病等</li>
</ul>

<h3>二、酸化土壤的判断</h3>

<h4>1. 土壤pH值测定</h4>

<ul>
    <li>使用pH试纸或便携式pH计进行快速检测</li>
    <li>采集0-20cm和20-40cm土壤样品送检，pH值低于5.5即为酸化土壤</li>
</ul>

<h4>2. 果树症状观察</h4>

<ul>
    <li>叶片发黄（尤其是叶脉间黄化），可能是铁、锰失调表现</li>
    <li>新梢生长较弱，节间缩短</li>
    <li>果实小，品质差，着色不良</li>
    <li>根系褐变，细根少，吸收能力弱</li>
</ul>

<h3>三、酸化土壤改良技术</h3>

<h4>1. 石灰性材料调节pH值</h4>

<ul>
    <li><strong>石灰施用</strong>：根据土壤pH值和质地确定用量
        <ul>
            <li>轻度酸化(pH 5.0-5.5)：每亩施用生石灰75-100公斤</li>
            <li>中度酸化(pH 4.5-5.0)：每亩施用生石灰100-150公斤</li>
            <li>重度酸化(pH &lt;4.5)：每亩施用生石灰150-200公斤</li>
        </ul>
    </li>
    <li><strong>施用方法</strong>：
        <ul>
            <li>沟施：在树冠投影外缘开环状沟，深20-30厘米，宽30厘米，将石灰与土壤混合后回填</li>
            <li>穴施：在树冠投影下开若干小穴，每穴深30厘米，施入石灰后覆土</li>
            <li>全园撒施：结合深翻，将石灰均匀撒施于果园土壤表面，再翻耕入土</li>
        </ul>
    </li>
    <li><strong>施用时间</strong>：以秋季落叶后至早春萌芽前为宜</li>
</ul>

<h4>2. 有机质改良</h4>

<ul>
    <li><strong>增施有机肥</strong>：每亩每年施用腐熟农家肥2000-3000公斤或商品有机肥500-800公斤</li>
    <li><strong>绿肥还田</strong>：种植紫云英、苕子等绿肥，翻耕还田</li>
    <li><strong>秸秆还田</strong>：将果园修剪枝条粉碎后还田，或引入其他作物秸秆</li>
    <li><strong>覆盖栽培</strong>：使用稻草、麦秸等有机物质覆盖果园</li>
</ul>

<h4>3. 生物炭应用</h4>

<ul>
    <li>每亩施用生物炭200-300公斤，可提高土壤pH值0.5-1.0个单位</li>
    <li>生物炭具有长效改良作用，可持续3-5年</li>
</ul>

<h4>4. 微生物制剂应用</h4>

<ul>
    <li>施用EM菌、光合细菌等微生物制剂，改善土壤微生物环境</li>
    <li>结合有机质施用，每亩用量按产品说明使用</li>
</ul>

<h3>四、合理施肥管理</h3>

<ul>
    <li><strong>减少酸性肥料使用</strong>：控制硫酸铵、过磷酸钙等酸性肥料用量</li>
    <li><strong>选用中性或碱性肥料</strong>：如尿素、碳酸氢铵、钙镁磷肥等</li>
    <li><strong>增施硅钙镁肥</strong>：补充钙、镁、硅等元素，提高土壤缓冲能力</li>
    <li><strong>平衡施肥</strong>：根据土壤测试结果，科学配比氮磷钾肥</li>
</ul>

<h3>五、水分管理</h3>

<ul>
    <li><strong>改善排水系统</strong>：防止果园积水，减少土壤淋溶作用</li>
    <li><strong>合理灌溉</strong>：尽量使用中性或偏碱性水源灌溉</li>
    <li><strong>水肥一体化</strong>：采用滴灌等节水灌溉技术，减少养分淋溶损失</li>
</ul>

<h3>六、分果树类型的改良要点</h3>

<h4>1. 柑橘类果园</h4>
<p>柑橘适宜在pH值5.5-6.5的土壤中生长，改良酸化土壤时要注意升pH不宜过快过高，以免引起微量元素缺乏。</p>

<h4>2. 苹果、梨等果园</h4>
<p>苹果适宜pH值为6.0-7.0，梨适宜pH值为6.0-7.5，可适当增加石灰用量。</p>

<h4>3. 蓝莓等喜酸果树</h4>
<p>蓝莓等少数喜酸性土壤的果树，pH值宜维持在4.5-5.5，不需要进行酸化土壤改良。</p>

<h3>七、改良效果评价</h3>

<ul>
    <li>定期监测土壤pH值变化</li>
    <li>观察果树生长状况和产量品质变化</li>
    <li>分析土壤养分有效性</li>
</ul>

<p>通过科学系统的酸化土壤改良，可以有效提高果园土壤质量，促进果树健康生长，提高果实产量和品质。</p>
            """,
            'category': category_objs[2],  # 土壤管理
            'tags': [tag_objs[3], tag_objs[12], tag_objs[7]]  # 果树、土壤改良、施肥
        },
        {
            'title': '有机蔬菜病虫害绿色防控技术',
            'content': """
<h2>有机蔬菜病虫害绿色防控技术</h2>

<p>有机蔬菜种植不允许使用化学合成农药和化肥，如何有效防控病虫害是有机蔬菜生产的核心技术之一。本文介绍有机蔬菜病虫害的绿色防控技术体系。</p>

<h3>一、有机蔬菜病虫害防控原则</h3>

<ul>
    <li><strong>预防为主</strong>：建立健康的种植环境，提高作物抗性</li>
    <li><strong>生态调控</strong>：利用生态系统的自我调节能力控制有害生物</li>
    <li><strong>多措并举</strong>：综合运用物理、生物、农业等多种防控手段</li>
    <li><strong>允许使用</strong>：只使用有机标准允许的防治资材</li>
</ul>

<h3>二、农业防控技术</h3>

<h4>1. 轮作与间作套种</h4>

<ul>
    <li><strong>合理轮作</strong>：不同科属蔬菜轮作，一般3-5年一个周期</li>
    <li><strong>间作套种</strong>：
        <ul>
            <li>葱蒜类与十字花科蔬菜间作，可减轻蚜虫危害</li>
            <li>茄果类与豆科作物间作，可减轻根结线虫病发生</li>
            <li>香草类植物(如万寿菊)与蔬菜间作，具有驱虫作用</li>
        </ul>
    </li>
</ul>

<h4>2. 健康种苗培育</h4>

<ul>
    <li>选择抗病品种，如抗病毒病的黄瓜品种、抗枯萎病的番茄品种等</li>
    <li>种子处理：
        <ul>
            <li>热水浸种：55℃温水浸种15-20分钟(十字花科蔬菜)</li>
            <li>生物制剂处理：使用枯草芽孢杆菌等微生物拌种</li>
            <li>植物提取物处理：大蒜素、茶籽饼等浸种</li>
        </ul>
    </li>
    <li>育苗基质处理：使用太阳能或蒸汽消毒育苗基质</li>
</ul>

<h4>3. 合理肥水管理</h4>

<ul>
    <li>使用腐熟有机肥，避免使用未腐熟有机物</li>
    <li>合理灌溉，避免田间积水，减少湿度</li>
    <li>控制氮肥用量，增施有机钾肥提高抗性</li>
</ul>

<h3>三、物理防控技术</h3>

<h4>1. 设施环境控制</h4>

<ul>
    <li>合理通风降湿，控制相对湿度低于85%</li>
    <li>保持适宜温度，避免温差过大</li>
</ul>

<h4>2. 物理阻隔</h4>

<ul>
    <li>防虫网覆盖：40-60目防虫网可阻隔蚜虫、白粉虱等</li>
    <li>反光膜铺设：银灰色反光膜可驱避蚜虫、蓟马</li>
    <li>防虫隔离带：在田间周围种植高大作物或设置隔离带</li>
</ul>

<h4>3. 诱控技术</h4>

<ul>
    <li>色板诱杀：黄板诱杀蚜虫、白粉虱，蓝板诱杀蓟马</li>
    <li>频振式杀虫灯：诱杀夜间活动害虫</li>
    <li>性信息素诱杀：使用性诱剂对付小菜蛾、斜纹夜蛾等</li>
</ul>

<h3>四、生物防控技术</h3>

<h4>1. 天敌昆虫利用</h4>

<ul>
    <li>释放捕食性天敌：如七星瓢虫、草蛉防治蚜虫</li>
    <li>释放寄生性天敌：如赤眼蜂防治鳞翅目害虫卵</li>
    <li>释放捕食螨：如智利小植绥螨防治红蜘蛛</li>
</ul>

<h4>2. 微生物农药应用</h4>

<ul>
    <li>细菌制剂：苏云金芽孢杆菌防治鳞翅目害虫</li>
    <li>真菌制剂：白僵菌防治蚜虫、粉虱</li>
    <li>病毒制剂：核型多角体病毒防治斜纹夜蛾等</li>
</ul>

<h4>3. 植物源农药应用</h4>

<ul>
    <li>烟碱类：烟草浸出液防治软体害虫</li>
    <li>除虫菊素类：万寿菊提取物防治多种害虫</li>
    <li>苦参碱：防治蚜虫、红蜘蛛等</li>
    <li>大蒜素：具有广谱抑菌作用</li>
</ul>

<h3>五、常见病害绿色防控方案</h3>

<h4>1. 病毒病防控</h4>

<ul>
    <li>控制传毒媒介昆虫（蚜虫、粉虱、蓟马）</li>
    <li>及时清除病株并带出田外销毁</li>
    <li>工具消毒：3%过氧乙酸溶液浸泡修剪工具</li>
    <li>喷施5%海藻酸或桔柠散增强植株抗性</li>
</ul>

<h4>2. 霜霉病防控</h4>

<ul>
    <li>合理通风降湿，保持叶面干燥</li>
    <li>使用铜制剂：波尔多液(1:1:100)或硫酸铜石灰混合剂</li>
    <li>生物制剂：枯草芽孢杆菌、木霉菌等微生物制剂</li>
</ul>

<h4>3. 根结线虫病防控</h4>

<ul>
    <li>轮作忌连作，与禾本科作物轮作</li>
    <li>种植万寿菊、芥菜等抑制线虫的植物</li>
    <li>土壤处理：太阳能土壤消毒</li>
    <li>使用有机肥+蘑菇渣发酵物改良土壤</li>
</ul>

<h3>六、常见害虫绿色防控方案</h3>

<h4>1. 蚜虫防控</h4>

<ul>
    <li>黄板诱杀成虫</li>
    <li>释放七星瓢虫、草蛉等天敌</li>
    <li>喷施苦参碱、除虫菊素等植物源制剂</li>
</ul>

<h4>2. 菜青虫防控</h4>

<ul>
    <li>频振式杀虫灯诱杀成虫</li>
    <li>释放赤眼蜂寄生卵</li>
    <li>喷施苏云金芽孢杆菌或核型多角体病毒制剂</li>
</ul>

<h4>3. 蓟马防控</h4>

<ul>
    <li>蓝色粘板诱杀成虫</li>
    <li>释放捕食螨防治</li>
    <li>喷施除虫菊素等植物源农药</li>
</ul>

<h3>七、有机蔬菜病虫害综合管理日常操作</h3>

<ul>
    <li><strong>定期巡检</strong>：每2-3天巡视一次，发现异常及时处理</li>
    <li><strong>环境管理</strong>：保持田间卫生，及时清除病残体</li>
    <li><strong>合理灌溉</strong>：宜早不宜晚，给水要适量</li>
    <li><strong>营养管理</strong>：适时追施腐熟有机肥，增强植株抵抗力</li>
    <li><strong>记录档案</strong>：详细记录防控措施和效果，为下季提供参考</li>
</ul>

<p>有机蔬菜病虫害绿色防控需要农业、物理、生物等多种措施综合运用，形成完整的防控体系。通过精细化管理，可以有效控制病虫害发生，生产出优质、安全的有机蔬菜。</p>
            """,
            'category': category_objs[3],  # 有机种植
            'tags': [tag_objs[4], tag_objs[5], tag_objs[9], tag_objs[10], tag_objs[16]]  # 蔬菜、有机栽培、病虫害、防治、生物防治
        },
        {
            'title': '微滴灌水肥一体化技术应用指南',
            'content': """
<h2>微滴灌水肥一体化技术应用指南</h2>

<p>微滴灌水肥一体化技术是集水分供应和养分管理于一体的现代农业高效灌溉施肥技术，能显著提高水肥利用效率，降低生产成本，提升作物产量和品质。本文详细介绍该技术的原理、设备组成、设计安装及应用管理要点。</p>

<h3>一、技术原理与优势</h3>

<h4>1. 基本原理</h4>

<p>微滴灌水肥一体化技术通过压力管道将水和可溶性肥料按需求配比，输送到作物根区，使作物获得均衡的水分和养分供应，达到精准控制水肥的目的。</p>

<h4>2. 主要优势</h4>

<ul>
    <li><strong>节水效果显著</strong>：与传统灌溉相比，节水30%-50%</li>
    <li><strong>提高肥料利用率</strong>：肥料利用率可提高30%-40%</li>
    <li><strong>减少环境污染</strong>：减少养分淋溶和流失，降低面源污染</li>
    <li><strong>提高作物产量和品质</strong>：产量增加10%-30%，品质明显提升</li>
    <li><strong>节省劳动力</strong>：实现灌溉施肥自动化，大幅降低劳动强度</li>
    <li><strong>适应性强</strong>：适用于各种地形条件和多种作物</li>
</ul>

<h3>二、系统组成与设备选择</h3>

<h4>1. 系统基本组成</h4>

<ul>
    <li><strong>水源部分</strong>：水源（井水、河水、水库等）、抽水设备</li>
    <li><strong>首部控制系统</strong>：过滤器、施肥器、水泵、控制阀门、水表等</li>
    <li><strong>输配水系统</strong>：干管、支管、毛管</li>
    <li><strong>滴头/滴带</strong>：实现水肥精准滴灌</li>
    <li><strong>自动控制系统</strong>：控制器、传感器、电磁阀等</li>
</ul>

<h4>2. 关键设备选择</h4>

<h5>过滤系统</h5>
<ul>
    <li>根据水源水质选择合适的过滤器：
        <ul>
            <li>砂石过滤器：适用于含沙量大的水源</li>
            <li>网式过滤器：适用于含杂质较少的清洁水源</li>
            <li>叠片过滤器：综合过滤性能好，应用广泛</li>
        </ul>
    </li>
    <li>过滤精度一般要求120目以上</li>
</ul>

<h5>施肥系统</h5>
<ul>
    <li>文丘里施肥器：结构简单，无需外接电源，但精确度较低</li>
    <li>比例泵：定量施肥，精度高，但需要电源</li>
    <li>压差施肥罐：成本适中，操作简便，适合中小规模种植</li>
</ul>

<h5>滴灌材料</h5>
<ul>
    <li>滴灌带：一次性使用，造价低，适合一年生作物</li>
    <li>内镶式滴头：使用寿命长，抗堵塞能力强，适合多年生作物</li>
    <li>滴头流量：选择0.8-3.0L/h，根据土壤和作物需水特性确定</li>
</ul>

<h3>三、系统设计与安装</h3>

<h4>1. 前期调查</h4>

<ul>
    <li>水源情况：水源类型、水质、水量、水压</li>
    <li>土壤情况：质地、结构、持水性能、渗透性</li>
    <li>地形条件：地面坡度、高低差</li>
    <li>作物种类：根系分布、需水特性、种植密度</li>
    <li>气候条件：降雨、温度、蒸发量等</li>
</ul>

<h4>2. 设计要点</h4>

<ul>
    <li><strong>水源规划</strong>：确保水源充足稳定，水质满足滴灌要求</li>
    <li><strong>管道布局</strong>：干管布置在地势较高处，支管顺坡或等高铺设</li>
    <li><strong>管道规格</strong>：根据流量和水压计算确定干支管直径</li>
    <li><strong>滴头布置</strong>：
        <ul>
            <li>大田作物：滴灌带沿作物行铺设</li>
            <li>果树：单株设置2-4个滴头，覆盖根系分布区</li>
            <li>蔬菜：一般每行作物设一条滴灌带</li>
        </ul>
    </li>
</ul>

<h4>3. 安装步骤</h4>

<ul>
    <li><strong>首部安装</strong>：安装水泵、过滤器、施肥器、阀门等，确保连接牢固</li>
    <li><strong>管道铺设</strong>：干管可埋入土中20-30cm，支管和毛管可地面铺设</li>
    <li><strong>滴灌带/滴头安装</strong>：按设计要求安装，确保位置准确</li>
    <li><strong>系统测试</strong>：检查系统是否漏水、堵塞，滴头是否正常工作</li>
</ul>

<h3>四、水肥管理技术</h3>

<h4>1. 灌溉管理</h4>

<ul>
    <li><strong>灌溉制度制定</strong>：
        <ul>
            <li>基于作物需水规律和土壤墒情确定灌溉量和灌溉频率</li>
            <li>一般原则：少量多次，保持土壤湿润但不过湿</li>
        </ul>
    </li>
    <li><strong>灌溉时间选择</strong>：宜在早晨或傍晚进行灌溉</li>
    <li><strong>灌溉周期参考</strong>：
        <ul>
            <li>沙质土壤：1-2天一次</li>
            <li>壤土：2-3天一次</li>
            <li>粘土：3-5天一次</li>
        </ul>
    </li>
</ul>

<h4>2. 施肥管理</h4>

<ul>
    <li><strong>适宜肥料选择</strong>：选用完全水溶性肥料，如尿素、硝酸钾、磷酸二氢钾等</li>
    <li><strong>肥料配方制定</strong>：根据作物需肥规律和土壤养分状况确定</li>
    <li><strong>施肥原则</strong>：少量多次，随水施肥</li>
    <li><strong>施肥操作要点</strong>：
        <ul>
            <li>先灌清水15-20分钟，湿润土壤</li>
            <li>然后进行水肥混合灌溉</li>
            <li>最后再灌清水15-20分钟，冲洗管道</li>
        </ul>
    </li>
</ul>

<h4>3. 不同作物的水肥管理要点</h4>

<h5>果树</h5>
<ul>
    <li>灌水量：成年果树每株每天10-20升</li>
    <li>施肥方案：以钾肥为主，磷肥次之，氮肥适量</li>
    <li>关键期：花前、坐果期、果实膨大期加大水肥供应</li>
</ul>

<h5>蔬菜</h5>
<ul>
    <li>灌水量：根据蒸发量和作物系数确定，一般每天2-4mm</li>
    <li>施肥方案：生长前期氮肥为主，中后期增加钾肥比例</li>
    <li>灌溉频率：一般1-2天一次，保持土壤湿润</li>
</ul>

<h5>大田作物</h5>
<ul>
    <li>灌水量：根据需水临界期确定，一般5-7天一次</li>
    <li>施肥方案：根据不同生长阶段调整氮磷钾比例</li>
</ul>

<h3>五、系统维护与故障排除</h3>

<h4>1. 日常维护</h4>

<ul>
    <li><strong>定期冲洗系统</strong>：每周冲洗主管和支管末端</li>
    <li><strong>检查过滤器</strong>：根据水质情况，1-7天清洗一次过滤器</li>
    <li><strong>检查滴头</strong>：定期检查滴头是否堵塞，工作是否正常</li>
    <li><strong>防止根系侵入</strong>：在滴灌末期适当增加滴灌频次，减少滴头干燥时间</li>
</ul>

<h4>2. 常见问题及解决方法</h4>

<ul>
    <li><strong>滴头堵塞</strong>：
        <ul>
            <li>物理堵塞：改进过滤系统</li>
            <li>化学堵塞：用酸性溶液（如稀释的柠檬酸）冲洗系统</li>
            <li>生物堵塞：用含氯消毒剂处理</li>
        </ul>
    </li>
    <li><strong>管道漏水</strong>：检查连接处，及时修补或更换</li>
    <li><strong>水压不足</strong>：检查水泵、管道是否有异常，调整系统分区</li>
</ul>

<h4>3. 季末处理</h4>

<ul>
    <li>收获后彻底清洗系统，用酸性溶液冲洗去除沉淀物</li>
    <li>滴灌带回收或妥善存放，避免阳光直射和鼠害</li>
    <li>设备检修，准备下一季使用</li>
</ul>

<h3>六、经济效益分析</h3>

<ul>
    <li><strong>投资成本</strong>：一般每亩投资1000-3000元（根据系统配置不同）</li>
    <li><strong>经济收益</strong>：
        <ul>
            <li>节水30%-50%，节约水费</li>
            <li>节肥20%-30%，节约肥料费</li>
            <li>节省人工50%以上</li>
            <li>增产10%-30%</li>
            <li>改善产品品质，提高经济效益</li>
        </ul>
    </li>
    <li><strong>投资回收期</strong>：一般1-3年可收回成本</li>
</ul>

<p>通过科学设计、规范安装和精细管理，微滴灌水肥一体化技术可显著提高农业生产效率和经济效益，是现代农业发展的重要技术手段。</p>
            """,
            'category': category_objs[4],  # 农业科技
            'tags': [tag_objs[12], tag_objs[14], tag_objs[6], tag_objs[7]]  # 农业机械、灌溉、节水技术、施肥
        }
    ]
    
    # 创建文章
    created_count = 0
    for article_data in articles:
        # 检查是否已存在同标题文章
        if not PlantingTechArticle.objects.filter(title=article_data['title']).exists():
            # 轮流使用不同的作者
            if created_count % 3 == 0:
                author = admin_user
            elif created_count % 3 == 1:
                author = expert_user
            else:
                author = farmer_user
                
            article = PlantingTechArticle.objects.create(
                title=article_data['title'],
                content=article_data['content'],
                author=author,  # 使用轮换的作者
                category=article_data['category'],
                views_count=random.randint(10, 200)
            )
            
            # 添加标签
            for tag in article_data['tags']:
                article.tags.add(tag)
            
            # 随机添加收藏
            favorite_count = random.randint(0, 10)
            users = list(CustomUser.objects.all()[:favorite_count+1])
            for user in users:
                article.favorite_user.add(user)
            
            created_count += 1
            print(f"已创建文章: {article_data['title']} (作者: {author.username})")
    
    print(f"总共创建了 {created_count} 篇新文章")
    return created_count

def verify_form_classes():
    """验证项目中的表单类配置是否正确"""
    from gannan_orange.forms import ReviewForm
    
    try:
        # 测试审核表单初始化
        test_form = ReviewForm()
        print("✅ 审核表单类验证成功")
    except Exception as e:
        print(f"❌ 审核表单类验证失败: {e}")
        
        # 检查是否存在不正确的表单类
        from django.apps import apps
        from django import forms
        
        for app_config in apps.get_app_configs():
            if hasattr(app_config, 'models_module'):
                forms_module_name = f"{app_config.name}.forms"
                try:
                    forms_module = __import__(forms_module_name, fromlist=[''])
                    for name in dir(forms_module):
                        obj = getattr(forms_module, name)
                        if isinstance(obj, type) and issubclass(obj, forms.Form) and obj != forms.Form:
                            # 检查是否以正确方式继承
                            if not issubclass(obj, forms.ModelForm) and hasattr(obj, '__init__'):
                                # 检查init方法是否处理instance参数
                                init_code = obj.__init__.__code__
                                if 'instance' in init_code.co_varnames:
                                    print(f"⚠️ 发现潜在问题表单类: {forms_module_name}.{name}")
                except ImportError:
                    continue
    
    # 检查是否存在ReviewForm和SomeOtherForm
    try:
        from gannan_orange.forms import ReviewForm
        print(f"✅ ReviewForm类存在，父类是: {ReviewForm.__bases__}")
        
        from gannan_orange.models import ReviewHistory
        print(f"✅ ReviewHistory模型存在")
    except (ImportError, AttributeError) as e:
        print(f"❌ 表单或模型导入失败: {e}")

if __name__ == "__main__":
    # 验证表单类和模型
    verify_form_classes()
    
    # 创建示例文章
    create_sample_articles()
