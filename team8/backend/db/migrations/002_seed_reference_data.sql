-- Sample provinces data (Major Iranian provinces)
INSERT INTO provinces (name, name_en, region) VALUES
    ('تهران', 'Tehran', 'Central'),
    ('اصفهان', 'Isfahan', 'Central'),
-- Sample provinces data (All 31 Iranian provinces)
INSERT INTO provinces (name, name_en) VALUES
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
ON CONFLICT (name) DO NOTHING;

-- Sample cities (Provincial capitals + major cities - 180+ cities)
INSERT INTO cities (province_id, name, name_en) VALUES
    -- Tehran Province (1)
    (1, 'تهران', 'Tehran'),
    (1, 'ری', 'Rey'),
    (1, 'شهریار', 'Shahriar'),
    (1, 'ورامین', 'Varamin'),
    (1, 'اسلامشهر', 'Eslamshahr'),
    (1, 'پاکدشت', 'Pakdasht'),
    (1, 'دماوند', 'Damavand'),
    (1, 'رباط‌کریم', 'Robat Karim'),
    
    -- Isfahan Province (2)
    (2, 'اصفهان', 'Isfahan'),
    (2, 'کاشان', 'Kashan'),
    (2, 'نجف‌آباد', 'Najafabad'),
    (2, 'خمینی‌شهر', 'Khomeinishahr'),
    (2, 'شاهین‌شهر', 'Shahinshahr'),
    (2, 'نطنز', 'Natanz'),
    (2, 'فلاورجان', 'Falavarjan'),
    (2, 'گلپایگان', 'Golpayegan'),
    (2, 'اردستان', 'Ardestan'),
    (2, 'نائین', 'Naein'),
    
    -- Fars Province (3)
    (3, 'شیراز', 'Shiraz'),
    (3, 'مرودشت', 'Marvdasht'),
    (3, 'جهرم', 'Jahrom'),
    (3, 'فسا', 'Fasa'),
    (3, 'لار', 'Lar'),
    (3, 'کازرون', 'Kazerun'),
    (3, 'داراب', 'Darab'),
    (3, 'نی‌ریز', 'Neyriz'),
    (3, 'آباده', 'Abadeh'),
    (3, 'فیروزآباد', 'Firuzabad'),
    
    -- Razavi Khorasan (4)
    (4, 'مشهد', 'Mashhad'),
    (4, 'نیشابور', 'Neyshabur'),
    (4, 'سبزوار', 'Sabzevar'),
    (4, 'تربت حیدریه', 'Torbat-e Heydarieh'),
    (4, 'قوچان', 'Quchan'),
    (4, 'گناباد', 'Gonabad'),
    (4, 'کاشمر', 'Kashmar'),
    (4, 'تربت جام', 'Torbat-e Jam'),
    (4, 'چناران', 'Chenaran'),
    
    -- East Azerbaijan (5)
    (5, 'تبریز', 'Tabriz'),
    (5, 'مرند', 'Marand'),
    (5, 'میانه', 'Mianeh'),
    (5, 'مراغه', 'Maragheh'),
    (5, 'اهر', 'Ahar'),
    (5, 'سراب', 'Sarab'),
    (5, 'شبستر', 'Shabestar'),
    (5, 'بناب', 'Bonab'),
    (5, 'ملکان', 'Malekan'),
    (5, 'عجب‌شیر', 'Ajabshir'),
    
    -- West Azerbaijan (6)
    (6, 'ارومیه', 'Urmia'),
    (6, 'خوی', 'Khoy'),
    (6, 'مهاباد', 'Mahabad'),
    (6, 'بوکان', 'Bukan'),
    (6, 'میاندوآب', 'Miandoab'),
    (6, 'سلماس', 'Salmas'),
    (6, 'نقده', 'Naqadeh'),
    (6, 'پیرانشهر', 'Piranshahr'),
    (6, 'ماکو', 'Maku'),
    
    -- Khuzestan (7)
    (7, 'اهواز', 'Ahvaz'),
    (7, 'آبادان', 'Abadan'),
    (7, 'خرمشهر', 'Khorramshahr'),
    (7, 'دزفول', 'Dezful'),
    (7, 'اندیمشک', 'Andimeshk'),
    (7, 'شوشتر', 'Shushtar'),
    (7, 'بهبهان', 'Behbahan'),
    (7, 'ماهشهر', 'Mahshahr'),
    (7, 'ایذه', 'Izeh'),
    (7, 'شوش', 'Shush'),
    (7, 'رامهرمز', 'Ramhormoz'),
    (7, 'هندیجان', 'Hendijan'),
    
    -- Gilan (8)
    (8, 'رشت', 'Rasht'),
    (8, 'بندر انزلی', 'Bandar Anzali'),
    (8, 'لاهیجان', 'Lahijan'),
    (8, 'لنگرود', 'Langarud'),
    (8, 'رودسر', 'Rudsar'),
    (8, 'تالش', 'Talesh'),
    (8, 'آستارا', 'Astara'),
    (8, 'صومعه‌سرا', 'Sowme''eh Sara'),
    (8, 'فومن', 'Fuman'),
    (8, 'ماسال', 'Masal'),
    
    -- Mazandaran (9)
    (9, 'ساری', 'Sari'),
    (9, 'بابل', 'Babol'),
    (9, 'آمل', 'Amol'),
    (9, 'قائمشهر', 'Qaem Shahr'),
    (9, 'نوشهر', 'Nowshahr'),
    (9, 'چالوس', 'Chalus'),
    (9, 'بابلسر', 'Babolsar'),
    (9, 'تنکابن', 'Tonekabon'),
    (9, 'رامسر', 'Ramsar'),
    (9, 'نکا', 'Neka'),
    (9, 'محمودآباد', 'Mahmudabad'),
    (9, 'بهشهر', 'Behshahr'),
    
    -- Kerman (10)
    (10, 'کرمان', 'Kerman'),
    (10, 'رفسنجان', 'Rafsanjan'),
    (10, 'سیرجان', 'Sirjan'),
    (10, 'بم', 'Bam'),
    (10, 'جیرفت', 'Jiroft'),
    (10, 'کهنوج', 'Kahnooj'),
    (10, 'زرند', 'Zarand'),
    (10, 'شهربابک', 'Shahrbabak'),
    (10, 'بافت', 'Baft'),
    (10, 'انار', 'Anar'),
    
    -- Hormozgan (11)
    (11, 'بندرعباس', 'Bandar Abbas'),
    (11, 'قشم', 'Qeshm'),
    (11, 'میناب', 'Minab'),
    (11, 'بندر لنگه', 'Bandar Lengeh'),
    (11, 'کیش', 'Kish'),
    (11, 'جاسک', 'Jask'),
    (11, 'بندر خمیر', 'Bandar Khamir'),
    (11, 'رودان', 'Rudan'),
    
    -- Sistan and Baluchestan (12)
    (12, 'زاهدان', 'Zahedan'),
    (12, 'زابل', 'Zabol'),
    (12, 'چابهار', 'Chabahar'),
    (12, 'ایرانشهر', 'Iranshahr'),
    (12, 'خاش', 'Khash'),
    (12, 'سراوان', 'Saravan'),
    (12, 'نیکشهر', 'Nikshahr'),
    
    -- Kurdistan (13)
    (13, 'سنندج', 'Sanandaj'),
    (13, 'سقز', 'Saqqez'),
    (13, 'مریوان', 'Marivan'),
    (13, 'بانه', 'Baneh'),
    (13, 'قروه', 'Qorveh'),
    (13, 'بیجار', 'Bijar'),
    (13, 'کامیاران', 'Kamyaran'),
    
    -- Hamadan (14)
    (14, 'همدان', 'Hamadan'),
    (14, 'ملایر', 'Malayer'),
    (14, 'نهاوند', 'Nahavand'),
    (14, 'تویسرکان', 'Tuyserkan'),
    (14, 'اسدآباد', 'Asadabad'),
    (14, 'بهار', 'Bahar'),
    (14, 'رزن', 'Razan'),
    
    -- Kermanshah (15)
    (15, 'کرمانشاه', 'Kermanshah'),
    (15, 'اسلام‌آباد غرب', 'Eslamabad-e Gharb'),
    (15, 'پاوه', 'Paveh'),
    (15, 'کنگاور', 'Kangavar'),
    (15, 'هرسین', 'Harsin'),
    (15, 'سنقر', 'Sonqor'),
    (15, 'جوانرود', 'Javanrud'),
    (15, 'قصر شیرین', 'Qasr-e Shirin'),
    
    -- Lorestan (16)
    (16, 'خرم‌آباد', 'Khorramabad'),
    (16, 'بروجرد', 'Borujerd'),
    (16, 'دورود', 'Dorud'),
    (16, 'الیگودرز', 'Aligudarz'),
    (16, 'ازنا', 'Azna'),
    (16, 'کوهدشت', 'Kuhdasht'),
    (16, 'نورآباد', 'Nurabad'),
    
    -- Markazi (17)
    (17, 'اراک', 'Arak'),
    (17, 'ساوه', 'Saveh'),
    (17, 'خمین', 'Khomein'),
    (17, 'محلات', 'Mahallat'),
    (17, 'دلیجان', 'Delijan'),
    (17, 'تفرش', 'Tafresh'),
    (17, 'شازند', 'Shazand'),
    
    -- Bushehr (18)
    (18, 'بوشهر', 'Bushehr'),
    (18, 'برازجان', 'Borazjan'),
    (18, 'کنگان', 'Kangan'),
    (18, 'گناوه', 'Genaveh'),
    (18, 'دیر', 'Deyr'),
    (18, 'دیلم', 'Deylam'),
    
    -- Zanjan (19)
    (19, 'زنجان', 'Zanjan'),
    (19, 'ابهر', 'Abhar'),
    (19, 'خدابنده', 'Khodabandeh'),
    (19, 'خرمدره', 'Khorramdarreh'),
    (19, 'ماهنشان', 'Mahneshan'),
    
    -- Semnan (20)
    (20, 'سمنان', 'Semnan'),
    (20, 'شاهرود', 'Shahroud'),
    (20, 'دامغان', 'Damghan'),
    (20, 'گرمسار', 'Garmsar'),
    (20, 'مهدی‌شهر', 'Mahdishahr'),
    
    -- Yazd (21)
    (21, 'یزد', 'Yazd'),
    (21, 'اردکان', 'Ardakan'),
    (21, 'میبد', 'Meybod'),
    (21, 'مهریز', 'Mehriz'),
    (21, 'تفت', 'Taft'),
    (21, 'ابرکوه', 'Abarkuh'),
    (21, 'بافق', 'Bafq'),
    
    -- Ardabil (22)
    (22, 'اردبیل', 'Ardabil'),
    (22, 'مشگین‌شهر', 'Meshgin Shahr'),
    (22, 'خلخال', 'Khalkhal'),
    (22, 'پارس‌آباد', 'Parsabad'),
    (22, 'گرمی', 'Germi'),
    (22, 'نمین', 'Namin'),
    (22, 'نیر', 'Nir'),
    
    -- Qom (23)
    (23, 'قم', 'Qom'),
    
    -- Qazvin (24)
    (24, 'قزوین', 'Qazvin'),
    (24, 'تاکستان', 'Takestan'),
    (24, 'آبیک', 'Abyek'),
    (24, 'بوئین‌زهرا', 'Buin Zahra'),
    (24, 'آوج', 'Avaj'),
    
    -- Golestan (25)
    (25, 'گرگان', 'Gorgan'),
    (25, 'گنبد کاووس', 'Gonbad-e Kavus'),
    (25, 'علی‌آباد', 'Aliabad'),
    (25, 'بندر ترکمن', 'Bandar Torkaman'),
    (25, 'آق‌قلا', 'Aqqala'),
    (25, 'کردکوی', 'Kordkuy'),
    (25, 'مینودشت', 'Minudasht'),
    (25, 'آزادشهر', 'Azadshahr'),
    
    -- North Khorasan (26)
    (26, 'بجنورد', 'Bojnord'),
    (26, 'شیروان', 'Shirvan'),
    (26, 'اسفراین', 'Esfarayen'),
    (26, 'جاجرم', 'Jajarm'),
    (26, 'راز و جرگلان', 'Raz va Jargalan'),
    
    -- South Khorasan (27)
    (27, 'بیرجند', 'Birjand'),
    (27, 'قائن', 'Qaen'),
    (27, 'فردوس', 'Ferdows'),
    (27, 'طبس', 'Tabas'),
    (27, 'نهبندان', 'Nehbandan'),
    (27, 'بشرویه', 'Boshruyeh'),
    
    -- Alborz (28)
    (28, 'کرج', 'Karaj'),
    (28, 'ساوجبلاغ', 'Savojbolagh'),
    (28, 'نظرآباد', 'Nazarabad'),
    (28, 'طالقان', 'Taleghan'),
    (28, 'اشتهارد', 'Eshtehard'),
    (28, 'فردیس', 'Fardis'),
    (28, 'هشتگرد', 'Hashtgerd'),
    
    -- Ilam (29)
    (29, 'ایلام', 'Ilam'),
    (29, 'ایوان', 'Ivan'),
    (29, 'دهلران', 'Dehloran'),
    (29, 'آبدانان', 'Abdanan'),
    (29, 'مهران', 'Mehran'),
    (29, 'دره‌شهر', 'Darreh Shahr'),
    
    -- Chaharmahal and Bakhtiari (30)
    (30, 'شهرکرد', 'Shahrekord'),
    (30, 'بروجن', 'Borujen'),
    (30, 'فارسان', 'Farsan'),
    (30, 'لردگان', 'Lordegan'),
    (30, 'اردل', 'Ardal'),
    
    -- Kohgiluyeh and Boyer-Ahmad (31)
    (31, 'یاسوج', 'Yasuj'),
    (31, 'دوگنبدان', 'Dogonbadan'),
    (31, 'دهدشت', 'Dehdasht'),
    (31, 'گچساران', 'Gachsaran'),
    (31, 'دنا', 'Dena')
ON CONFLICT (province_id, name) DO NOTHING;

-- Sample categories data
INSERT INTO categories (name, name_en) VALUES
    ('تاریخی', 'Historical'),
    ('طبیعی', 'Nature'),
    ('مذهبی', 'Religious'),
    ('فرهنگی', 'Cultural'),
    ('رستوران', 'Restaurant'),
    ('کافه', 'Cafe'),
    ('هتل', 'Hotel'),
    ('پارک', 'Park'),
    ('موزه', 'Museum'),
    ('بازار', 'Bazaar')
ON CONFLICT (name) DO NOTHING;