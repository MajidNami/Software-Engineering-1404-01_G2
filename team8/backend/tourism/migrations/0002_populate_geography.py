from django.db import migrations

def populate_geography(apps, schema_editor):
    Province = apps.get_model('tourism', 'Province') 
    City = apps.get_model('tourism', 'City')
    Category = apps.get_model('tourism', 'Category')

    # CATEGORIES
    categories_data = [
        ('تاریخی', 'Historical'),
        ('طبیعی', 'Nature'), 
        ('مذهبی', 'Religious'),
        ('فرهنگی', 'Cultural'),
        ('رستوران', 'Restaurant'),
        ('کافه', 'Cafe'),
        ('هتل', 'Hotel'),
        ('پارک', 'Park'),
        ('موزه', 'Museum'),
        ('بازار', 'Bazaar'),
        ('مدرن', 'Modern'),       
        ('تفریحی', 'Recreational'), 
    ]

    for name_fa, name_en in categories_data:
        Category.objects.get_or_create(name=name_fa, defaults={'name_en': name_en})

    # PROVINCES
    provinces_data = [
        ('تهران', 'Tehran'),
        ('اصفهان', 'Isfahan'),
        ('فارس', 'Fars'),
        ('خراسان رضوی', 'Razavi Khorasan'),
        ('آذربایجان شرقی', 'East Azerbaijan'),
        ('آذربایجان غربی', 'West Azerbaijan'),
        ('خوزستان', 'Khuzestan'),
        ('گیلان', 'Gilan'),
        ('مازندران', 'Mazandaran'),
        ('کرمان', 'Kerman'),
        ('هرمزگان', 'Hormozgan'),
        ('سیستان و بلوچستان', 'Sistan and Baluchestan'),
        ('کردستان', 'Kurdistan'),
        ('همدان', 'Hamadan'),
        ('کرمانشاه', 'Kermanshah'),
        ('لرستان', 'Lorestan'),
        ('مرکزی', 'Markazi'),
        ('بوشهر', 'Bushehr'),
        ('زنجان', 'Zanjan'),
        ('سمنان', 'Semnan'),
        ('یزد', 'Yazd'),
        ('اردبیل', 'Ardabil'),
        ('قم', 'Qom'),
        ('قزوین', 'Qazvin'),
        ('گلستان', 'Golestan'),
        ('خراسان شمالی', 'North Khorasan'),
        ('خراسان جنوبی', 'South Khorasan'),
        ('البرز', 'Alborz'),
        ('ایلام', 'Ilam'),
        ('چهارمحال و بختیاری', 'Chaharmahal and Bakhtiari'),
        ('کهگیلویه و بویراحمد', 'Kohgiluyeh and Boyer-Ahmad')
    ]

    prov_map = {} 
    for name_fa, name_en in provinces_data:
        p, _ = Province.objects.get_or_create(name=name_fa, defaults={'name_en': name_en})
        prov_map[name_fa] = p


    # CITIES
    # Format: (Province Name, [List of (City Name, English Name)])
    
    cities_structure = [
        ('تهران', [
            ('تهران', 'Tehran'), ('ری', 'Rey'), ('شهریار', 'Shahriar'), 
            ('ورامین', 'Varamin'), ('اسلامشهر', 'Eslamshahr'), ('پاکدشت', 'Pakdasht'), 
            ('دماوند', 'Damavand'), ('رباط‌کریم', 'Robat Karim'),
            ('شمیرانات', 'Shemiranat'),
        ]),
        ('اصفهان', [
            ('اصفهان', 'Isfahan'), ('کاشان', 'Kashan'), ('نجف‌آباد', 'Najafabad'), 
            ('خمینی‌شهر', 'Khomeinishahr'), ('شاهین‌شهر', 'Shahinshahr'), ('نطنز', 'Natanz'), 
            ('فلاورجان', 'Falavarjan'), ('گلپایگان', 'Golpayegan'), ('اردستان', 'Ardestan'), ('نائین', 'Naein'),
            ('ابیانه', 'Abyaneh'),
        ]),
        ('فارس', [
            ('شیراز', 'Shiraz'), ('مرودشت', 'Marvdasht'), ('جهرم', 'Jahrom'), 
            ('فسا', 'Fasa'), ('لار', 'Lar'), ('کازرون', 'Kazerun'), 
            ('داراب', 'Darab'), ('نی‌ریز', 'Neyriz'), ('آباده', 'Abadeh'), ('فیروزآباد', 'Firuzabad'),
        ]),
        ('خراسان رضوی', [
            ('مشهد', 'Mashhad'), ('نیشابور', 'Neyshabur'), ('سبزوار', 'Sabzevar'), 
            ('تربت حیدریه', 'Torbat-e Heydarieh'), ('قوچان', 'Quchan'), ('گناباد', 'Gonabad'), 
            ('کاشمر', 'Kashmar'), ('تربت جام', 'Torbat-e Jam'), ('چناران', 'Chenaran'),
            ('کلات', 'Kalat'),
        ]),
        ('آذربایجان شرقی', [
            ('تبریز', 'Tabriz'), ('مرند', 'Marand'), ('میانه', 'Mianeh'), 
            ('مراغه', 'Maragheh'), ('اهر', 'Ahar'), ('سراب', 'Sarab'), 
            ('شبستر', 'Shabestar'), ('بناب', 'Bonab'), ('ملکان', 'Malekan'), ('عجب‌شیر', 'Ajabshir'),
        ]),
        ('آذربایجان غربی', [
            ('ارومیه', 'Urmia'), ('خوی', 'Khoy'), ('مهاباد', 'Mahabad'), 
            ('بوکان', 'Bukan'), ('میاندوآب', 'Miandoab'), ('سلماس', 'Salmas'), 
            ('نقده', 'Naqadeh'), ('پیرانشهر', 'Piranshahr'), ('ماکو', 'Maku'),
            ('تکاب', 'Takab'), ('چالدران', 'Chaldran'),
        ]),
        ('خوزستان', [
            ('اهواز', 'Ahvaz'), ('آبادان', 'Abadan'), ('خرمشهر', 'Khorramshahr'), 
            ('دزفول', 'Dezful'), ('اندیمشک', 'Andimeshk'), ('شوشتر', 'Shushtar'), 
            ('بهبهان', 'Behbahan'), ('ماهشهر', 'Mahshahr'), ('ایذه', 'Izeh'), 
            ('شوش', 'Shush'), ('رامهرمز', 'Ramhormoz'), ('هندیجان', 'Hendijan'),
        ]),
        ('گیلان', [
            ('رشت', 'Rasht'), ('بندر انزلی', 'Bandar Anzali'), ('لاهیجان', 'Lahijan'), 
            ('لنگرود', 'Langarud'), ('رودسر', 'Rudsar'), ('تالش', 'Talesh'), 
            ('آستارا', 'Astara'), ('صومعه‌سرا', 'Sowme''eh Sara'), ('فومن', 'Fuman'), ('ماسال', 'Masal'),
        ]),
        ('مازندران', [
            ('ساری', 'Sari'), ('بابل', 'Babol'), ('آمل', 'Amol'), 
            ('قائمشهر', 'Qaem Shahr'), ('نوشهر', 'Nowshahr'), ('چالوس', 'Chalus'), 
            ('بابلسر', 'Babolsar'), ('تنکابن', 'Tonekabon'), ('رامسر', 'Ramsar'), 
            ('نکا', 'Neka'), ('محمودآباد', 'Mahmudabad'), ('بهشهر', 'Behshahr'),
            ('کلاردشت', 'Kelardasht'),
        ]),
        ('کرمان', [
            ('کرمان', 'Kerman'), ('رفسنجان', 'Rafsanjan'), ('سیرجان', 'Sirjan'), 
            ('بم', 'Bam'), ('جیرفت', 'Jiroft'), ('کهنوج', 'Kahnooj'), 
            ('زرند', 'Zarand'), ('شهربابک', 'Shahrbabak'), ('بافت', 'Baft'), ('انار', 'Anar'),
            ('ماهان', 'Mahan'), ('شهداد', 'Shahdad'),
        ]),
        ('هرمزگان', [
            ('بندرعباس', 'Bandar Abbas'), ('قشم', 'Qeshm'), ('میناب', 'Minab'), 
            ('بندر لنگه', 'Bandar Lengeh'), ('کیش', 'Kish'), ('جاسک', 'Jask'), 
            ('بندر خمیر', 'Bandar Khamir'), ('رودان', 'Rudan'),
            ('جزیره کیش', 'Kish Island'), ('جزیره قشم', 'Qeshm Island'), 
            ('جزیره لارک', 'Lark Island'), ('جزیره هنگام', 'Hengam Island'),
        ]),
        ('سیستان و بلوچستان', [
            ('زاهدان', 'Zahedan'), ('زابل', 'Zabol'), ('چابهار', 'Chabahar'), 
            ('ایرانشهر', 'Iranshahr'), ('خاش', 'Khash'), ('سراوان', 'Saravan'), ('نیکشهر', 'Nikshahr'),
        ]),
        ('کردستان', [
            ('سنندج', 'Sanandaj'), ('سقز', 'Saqqez'), ('مریوان', 'Marivan'), 
            ('بانه', 'Baneh'), ('قروه', 'Qorveh'), ('بیجار', 'Bijar'), ('کامیاران', 'Kamyaran'),
            ('دیواندره', 'Divandarreh'), ('سروآباد', 'Sarvabad'),
        ]),
        ('همدان', [
            ('همدان', 'Hamadan'), ('ملایر', 'Malayer'), ('نهاوند', 'Nahavand'), 
            ('تویسرکان', 'Tuyserkan'), ('اسدآباد', 'Asadabad'), ('بهار', 'Bahar'), ('رزن', 'Razan'),
        ]),
        ('کرمانشاه', [
            ('کرمانشاه', 'Kermanshah'), ('اسلام‌آباد غرب', 'Eslamabad-e Gharb'), 
            ('پاوه', 'Paveh'), ('کنگاور', 'Kangavar'), ('هرسین', 'Harsin'), 
            ('سنقر', 'Sonqor'), ('جوانرود', 'Javanrud'), ('قصر شیرین', 'Qasr-e Shirin'),
            ('سرپل ذهاب', 'Sarpol-e Zahab'), ('روانسر', 'Ravansar'),
        ]),
        ('لرستان', [
            ('خرم‌آباد', 'Khorramabad'), ('بروجرد', 'Borujerd'), ('دورود', 'Dorud'), 
            ('الیگودرز', 'Aligudarz'), ('ازنا', 'Azna'), ('کوهدشت', 'Kuhdasht'), ('نورآباد', 'Nurabad'),
        ]),
        ('مرکزی', [
            ('اراک', 'Arak'), ('ساوه', 'Saveh'), ('خمین', 'Khomein'), 
            ('محلات', 'Mahallat'), ('دلیجان', 'Delijan'), ('تفرش', 'Tafresh'), ('شازند', 'Shazand'),
        ]),
        ('بوشهر', [
            ('بوشهر', 'Bushehr'), ('برازجان', 'Borazjan'), ('کنگان', 'Kangan'), 
            ('گناوه', 'Genaveh'), ('دیر', 'Deyr'), ('دیلم', 'Deylam'),
            ('بندر سیراف', 'Bandar Siraf'),
        ]),
        ('زنجان', [
            ('زنجان', 'Zanjan'), ('ابهر', 'Abhar'), ('خدابنده', 'Khodabandeh'), 
            ('خرمدره', 'Khorramdarreh'), ('ماهنشان', 'Mahneshan'),
            ('سلطانیه', 'Soltaniyeh'),
        ]),
        ('سمنان', [
            ('سمنان', 'Semnan'), ('شاهرود', 'Shahroud'), ('دامغان', 'Damghan'), 
            ('گرمسار', 'Garmsar'), ('مهدی‌شهر', 'Mahdishahr'),
        ]),
        ('یزد', [
            ('یزد', 'Yazd'), ('اردکان', 'Ardakan'), ('میبد', 'Meybod'), 
            ('مهریز', 'Mehriz'), ('تفت', 'Taft'), ('ابرکوه', 'Abarkuh'), ('بافق', 'Bafq'),
            ('زارچ', 'Zarch'), ('اشکذر', 'Ashkezar'),
        ]),
        ('اردبیل', [
            ('اردبیل', 'Ardabil'), ('مشگین‌شهر', 'Meshgin Shahr'), ('خلخال', 'Khalkhal'), 
            ('پارس‌آباد', 'Parsabad'), ('گرمی', 'Germi'), ('نمین', 'Namin'), ('نیر', 'Nir'),
        ]),
        ('قم', [
            ('قم', 'Qom'),
        ]),
        ('قزوین', [
            ('قزوین', 'Qazvin'), ('تاکستان', 'Takestan'), ('آبیک', 'Abyek'), 
            ('بوئین‌زهرا', 'Buin Zahra'), ('آوج', 'Avaj'),
        ]),
        ('گلستان', [
            ('گرگان', 'Gorgan'), ('گنبد کاووس', 'Gonbad-e Kavus'), ('علی‌آباد', 'Aliabad'), 
            ('بندر ترکمن', 'Bandar Torkaman'), ('آق‌قلا', 'Aqqala'), ('کردکوی', 'Kordkuy'), 
            ('مینودشت', 'Minudasht'), ('آزادشهر', 'Azadshahr'),
            ('علی آباد کتول', 'Aliabad-e Katul'), ('گالیکش', 'Galikesh'),
        ]),
        ('خراسان شمالی', [
            ('بجنورد', 'Bojnord'), ('شیروان', 'Shirvan'), ('اسفراین', 'Esfarayen'), 
            ('جاجرم', 'Jajarm'), ('راز و جرگلان', 'Raz va Jargalan'),
        ]),
        ('خراسان جنوبی', [
            ('بیرجند', 'Birjand'), ('قائن', 'Qaen'), ('فردوس', 'Ferdows'), 
            ('طبس', 'Tabas'), ('نهبندان', 'Nehbandan'), ('بشرویه', 'Boshruyeh'),
            ('سربیشه', 'Sarbisheh'),
        ]),
        ('البرز', [
            ('کرج', 'Karaj'), ('ساوجبلاغ', 'Savojbolagh'), ('نظرآباد', 'Nazarabad'), 
            ('طالقان', 'Taleghan'), ('اشتهارد', 'Eshtehard'), ('فردیس', 'Fardis'), 
            ('هشتگرد', 'Hashtgerd'),
        ]),
        ('ایلام', [
            ('ایلام', 'Ilam'), ('ایوان', 'Ivan'), ('دهلران', 'Dehloran'), 
            ('آبدانان', 'Abdanan'), ('مهران', 'Mehran'), ('دره‌شهر', 'Darreh Shahr'),
        ]),
        ('چهارمحال و بختیاری', [
            ('شهرکرد', 'Shahrekord'), ('بروجن', 'Borujen'), ('فارسان', 'Farsan'), 
            ('لردگان', 'Lordegan'), ('اردل', 'Ardal'),
            ('کوهرنگ', 'Koohrang'),
        ]),
        ('کهگیلویه و بویراحمد', [
            ('یاسوج', 'Yasuj'), ('دوگنبدان', 'Dogonbadan'), ('دهدشت', 'Dehdasht'), 
            ('گچساران', 'Gachsaran'), ('دنا', 'Dena'),
        ]),
    ]

    for prov_name, cities in cities_structure:
        province = prov_map.get(prov_name)
        if province:
            for city_name, city_name_en in cities:
                City.objects.get_or_create(
                    name=city_name,
                    province=province,
                    defaults={'name_en': city_name_en}
                )

class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_geography),
    ]