"""
Seed service for constituencies and wards data.
Uses data extracted from frontend kenyaLocations.ts
"""

KENYA_CONSTITUENCIES_WARDS = {
    'Baringo': {
        'Baringo Central': ['Kabarnet', 'Sacho', 'Tenges', 'Ewalel/Chapchap', 'Kapropita'],
        'Baringo North': ['Barwessa', 'Kabartonjo', 'Saimo-Kipsaraman', 'Saimo-Soi', 'Bartabwa'],
        'Baringo South': ['Marigat', 'Ilchamus', 'Mochongoi', 'Mukutani'],
        'Eldama Ravine': ['Eldama Ravine', 'Lembus', 'Lembus-Kwen', 'Ravine', 'Koibatek', 'Mumberes/Maji Mazuri'],
        'Mogotio': ['Mogotio', 'Emining', 'Kisanana'],
        'Tiaty': ['Tirioko', 'Kolowa', 'Ribkwo', 'Silale', 'Loiyamorok', 'Tangulbei/Korossi', 'Churo/Amaya']
    },
    'Bomet': {
        'Bomet Central': ['Silibwet Township', 'Ndaraweta', 'Singorwet', 'Chesoen', 'Mutarakwa'],
        'Bomet East': ['Merigi', 'Kembu', 'Longisa', 'Kipreres', 'Chemaner'],
        'Chepalungu': ['Kongasis', 'Nyangores', 'Sigor', 'Chebunyo', 'Siongiroi'],
        'Konoin': ['Chepchabas', 'Kimulot', 'Mogogosiek', 'Boito', 'Embomos'],
        'Sotik': ['Ndanai/Abosi', 'Chemagel', 'Kipsonoi', 'Kapletundo', 'Rongena/Manaret']
    },
    'Bungoma': {
        'Bumula': ['Bumula', 'Khasoko', 'Kabula', 'Kimaeti', 'South Bukusu', 'Siboti'],
        'Kabuchai': ['West Nalondo', 'Bwake/Luuya', 'Mukuyuni', 'East Kabuchai', 'West Kabuchai', 'Chwele/Kabula'],
        'Kanduyi': ['Khalaba', 'Bukembe West', 'Bukembe East', 'Township', 'Musikoma', 'East Sang\'alo', 'Marakaru/Tuuti', 'West Sang\'alo'],
        'Kimilili': ['Kimilili', 'Kibingei', 'Maeni', 'Kamukuywa'],
        'Mt Elgon': ['Cheptais', 'Chesikaki', 'Chepyuk', 'Kapkateny', 'Kaptama', 'Elgon'],
        'Sirisia': ['Namwela', 'Malakisi/South Kulisiru', 'Lwandanyi'],
        'Tongaren': ['Mbakalo', 'Naitiri/Kabuyefwe', 'Milima', 'Ndalu/Tabani', 'Tongaren', 'Soysambu/Mitua'],
        'Webuye East': ['Mihuu', 'Ndivisi', 'Maraka'],
        'Webuye West': ['Sitikho', 'Matulo', 'Bokoli', 'Misikhu']
    },
    'Busia': {
        'Budalangi': ['Bunyala South', 'Bunyala Central', 'Bunyala North', 'Bunyala West'],
        'Butula': ['Marachi West', 'Kingandole', 'Marachi Central', 'Marachi East', 'Marachi North', 'Elugulu'],
        'Funyula': ['Namboboto Nambuku', 'Nangina', 'Ageng\'a Nanguba', 'Bwiri'],
        'Matayos': ['Bukhayo East', 'Burumba', 'Bukhayo Central', 'Mayenje', 'Bukhayo North/Waltsi', 'Bukhayo West'],
        'Nambale': ['Nambale Township', 'Bukhayo South', 'Malaba South', 'Malaba Central', 'Malaba North'],
        'Samia': ['Nangoma', 'Agenga Ager', 'Bwiri'],
        'Teso North': ['Malaba Township', 'Angurai South', 'Angurai North', 'Angurai East', 'Amukura West', 'Amukura East', 'Amukura Central'],
        'Teso South': ['Chakol South', 'Chakol North', 'Amukura South', 'Amukura Central', 'Amukura East']
    },
    'Elgeyo-Marakwet': {
        'Keiyo North': ['Emsoo', 'Kamariny', 'Kapchemutwa', 'Tambach'],
        'Keiyo South': ['Kaptarakwa', 'Chepkorio', 'Soy North', 'Soy South', 'Kabiemit', 'Metkei'],
        'Marakwet East': ['Kapyego', 'Sambirir', 'Endo', 'Embobut/Embulot'],
        'Marakwet West': ['Lelan', 'Sengwer', 'Cherang\'any/Chebororwa', 'Moiben/Kuserwo', 'Kapsowar', 'Arror']
    },
    'Embu': {
        'Manyatta': ['Ruguru/Ngandori', 'Kithimu', 'Nginda', 'Mbeti North', 'Kirimari', 'Gaturi South', 'Gaturi North'],
        'Mbeere North': ['Nthawa', 'Muminji', 'Evurore', 'Mwea'],
        'Mbeere South': ['Mwea', 'Makima', 'Mbeti South', 'Mavuria', 'Kiambere'],
        'Runyenjes': ['Gaturi South', 'Kagaari South', 'Central Ward', 'Kagaari North', 'Kyeni North', 'Kyeni South']
    },
    'Garissa': {
        'Balambala': ['Balambala', 'Danyere', 'Jara Jara', 'Saka', 'Sankuri'],
        'Dadaab': ['Dertu', 'Dadaab', 'Labisley', 'Damajale', 'Liboi', 'Abakaile'],
        'Fafi': ['Bura', 'Dekaharia', 'Jarajila', 'Fafi', 'Nanighi'],
        'Garissa Township': ['Waberi', 'Galbet', 'Township', 'Iftin'],
        'Ijara': ['Ijara', 'Masalani', 'Sangailu', 'Hulugho'],
        'Lagdera': ['Modogashe', 'Benane', 'Goreale', 'Maalimin', 'Sabena', 'Baraki']
    },
    'Homa Bay': {
        'Homa Bay Town': ['Homa Bay Arujo', 'Homa Bay West', 'Homa Bay Central', 'Homa Bay East'],
        'Kabondo Kasipul': ['West Kabondo', 'East Kabondo', 'West Kasipul', 'South Kasipul'],
        'Karachuonyo': ['West Karachuonyo', 'North Karachuonyo', 'Kibiri', 'Wangchieng', 'Kendu Bay Town', 'Kanyaluo'],
        'Kasipul': ['West Kasipul', 'South Kasipul', 'Central Kasipul', 'East Kamagak', 'West Kamagak'],
        'Mbita': ['Mfangano Island', 'Rusinga Island', 'Kasgunga', 'Gembe', 'Lambwe'],
        'Ndhiwa': ['Kwabwai', 'Kanyadoto', 'Kanyakela', 'Kabuoch North', 'Kabuoch South/Pala', 'Kanyamwa Kologi', 'Kanyamwa Kosewe'],
        'Rangwe': ['West Gem', 'Central Gem', 'Kagan', 'Kochia'],
        'Suba North': ['Suba Central', 'Gwassi South', 'Gwassi North', 'Kaksingri West', 'Kaksingri East', 'Ruma-Kaksingri'],
        'Suba South': ['Gwassi South', 'Gwassi North', 'Kaksingri West']
    },
    'Isiolo': {
        'Isiolo North': ['Wabera', 'Bulla Pesa', 'Chari', 'Cherab', 'Ngare Mara', 'Burat', 'Oldonyiro'],
        'Isiolo South': ['Garbatulla', 'Kinna', 'Sericho']
    },
    'Kajiado': {
        'Kajiado Central': ['Purko', 'Ildamat', 'Dalalekutuk', 'Matapato North', 'Matapato South'],
        'Kajiado East': ['Kaputiei North', 'Kitengela', 'Oloosirkon/Sholinke', 'Kenyawa-Poka', 'Imaroro'],
        'Kajiado North': ['Olkeri', 'Ongata Rongai', 'Nkaimurunya', 'Oloolua', 'Ngong'],
        'Kajiado South': ['Entonet/Lenkism', 'Mbirikani/Eselenzkel', 'Kuku', 'Rombo', 'Kimana'],
        'Kajiado West': ['Keekonyokie', 'Iloodokilani', 'Magadi', 'Ewuaso Oo Nkidong\'i', 'Mosiro']
    },
    'Kakamega': {
        'Butere': ['Marama West', 'Marama Central', 'Marama North', 'Marama South', 'Marenyo-Shianda'],
        'Ikolomani': ['Idakho South', 'Idakho East', 'Idakho North', 'Idakho Central'],
        'Khwisero': ['Kisa North', 'Kisa East', 'Kisa West', 'Kisa Central'],
        'Likuyani': ['Likuyani', 'Sango', 'Kongoni', 'Nzoia', 'Sinoko'],
        'Lugari': ['Mautuma', 'Lugari', 'Lumakanda', 'Chekalini', 'Chevaywa', 'Lwandeti'],
        'Lurambi': ['Butsotso East', 'Butsotso South', 'Butsotso Central', 'Shieywe', 'Mahiakalo', 'Shirere'],
        'Malava': ['West Kabras', 'Chemuche', 'East Kabras', 'Butali/Chegulo', 'Manda-Shivanga', 'South Kabras'],
        'Matungu': ['Koyonzo', 'Kholera', 'Khalaba', 'Mayoni', 'Namamali'],
        'Mumias East': ['East Wanga', 'Malaha/Isongo/Makunga', 'Lusheya/Lubinu'],
        'Mumias West': ['Mumias Central', 'Mumias North', 'Etenje', 'Musanda'],
        'Navakholo': ['Ingostse-Mathia', 'Shinoyi-Shikomari-Esumeyia', 'Bunyala West', 'Bunyala East', 'Bunyala Central'],
        'Shinyalu': ['Murhanda', 'Isukha North', 'Isukha Central', 'Isukha South', 'Isukha East', 'Isukha West']
    },
    'Kericho': {
        'Ainamoi': ['Kapsoit', 'Ainamoi', 'Kapkugerwet', 'Kipchebor', 'Kipchimchim', 'Kapsaos'],
        'Belgut': ['Kapsuser', 'Chemosot', 'Cheptororiet/Seretut', 'Chaik', 'Waldai', 'Kabianga'],
        'Bureti': ['Kisiara', 'Tebesonik', 'Cheboin', 'Litein', 'Kembu', 'Kapkatet'],
        'Kipkelion East': ['Londiani', 'Kedowa/Kimugul', 'Chepseon', 'Tendeno/Sorget'],
        'Kipkelion West': ['Kunyak', 'Kamasian', 'Kipkelion', 'Chilchila'],
        'Sigowet/Soin': ['Sigowet', 'Kaplelartet', 'Soliat', 'Soin']
    },
    'Kiambu': {
        'Gatundu North': ['Gituamba', 'Githobokoni', 'Chania', 'Mang\'u', 'Ting\'ang\'a'],
        'Gatundu South': ['Kiganjo', 'Ndarugu', 'Ngenda', 'Kirwara', 'Kanundu'],
        'Githunguri': ['Githunguri', 'Githiga', 'Ikinu', 'Ngewa', 'Komothai'],
        'Juja': ['Murera', 'Theta', 'Juja', 'Witeithie', 'Kalimoni'],
        'Kabete': ['Gitaru', 'Muguga', 'Nyadhuna', 'Kabete', 'Uthiru'],
        'Kiambaa': ['Cianda', 'Karuri', 'Ndenderu', 'Muchatha', 'Kihara'],
        'Kiambu Town': ['Township', 'Ting\'ang\'a', 'Ndumberi', 'Riabai'],
        'Kikuyu': ['Karai', 'Nachu', 'Sigona', 'Kikuyu', 'Kinoo'],
        'Lari': ['Kinale', 'Kijabe', 'Nyanduma', 'Kamburu', 'Lari/Kirenga'],
        'Limuru': ['Bibirioni', 'Limuru East', 'Limuru Central', 'Ndeiya', 'Ngecha Tigoni'],
        'Ruiru': ['Gitothua', 'Biashara', 'Gatongora', 'Kahawa Sukari', 'Kahawa Wendani', 'Kiuu', 'Mwiki', 'Mwihoko'],
        'Thika Town': ['Township', 'Kamenu', 'Hospital', 'Gatuanyaga', 'Ngoliba']
    },
    'Kilifi': {
        'Ganze': ['Bamba', 'Jaribuni', 'Sokoke', 'Ganze', 'Dungicha'],
        'Kaloleni': ['Mariakani', 'Kayafungo', 'Kaloleni', 'Mwanamwinga'],
        'Kilifi North': ['Tezo', 'Sokoni', 'Kibarani', 'Dabaso', 'Matsangoni', 'Watamu', 'Mnarani'],
        'Kilifi South': ['Junju', 'Mwarakaya', 'Shimo la Tewa', 'Chasimba', 'Mtepeni'],
        'Magarini': ['Marafa', 'Magarini', 'Gongoni', 'Adu', 'Garashi'],
        'Malindi': ['Jilore', 'Kakuyuni', 'Ganda', 'Malindi Town', 'Shella'],
        'Rabai': ['Mwawesa', 'Ruruma', 'Kambe/Ribe', 'Rabai/Kisurutini']
    },
    'Kirinyaga': {
        'Gichugu': ['Kabare', 'Baragwi', 'Njukiini', 'Ngariama', 'Karumandi'],
        'Kirinyaga Central': ['Mutithi', 'Kanyekiini', 'Kerugoya', 'Inoi'],
        'Mwea': ['Mutithi', 'Kangai', 'Wamumu', 'Nyangati', 'Murinduko', 'Gathigiriri', 'Tebere'],
        'Ndia': ['Mukure', 'Kiine', 'Kariti', 'Kibirigwi', 'Thiba', 'Karira']
    },
    'Kisii': {
        'Bobasi': ['Masige West', 'Masige East', 'Basi Central', 'Nyacheki', 'Basi Bogetaorio', 'Basi Chache', 'Basi Borabu/S.Mugirango B'],
        'Bomachoge Borabu': ['Bomariba', 'Bosoti/Sengera'],
        'Bomachoge Chache': ['Majoge Basi', 'Boochi/Tendere', 'Bosoti/Sengera'],
        'Bonchari': ['Tabaka', 'Bogiakumu', 'Boikanga', 'Bomorenda', 'Riana'],
        'Kitutu Chache North': ['Monyerero', 'Sensi', 'Marani', 'Kegogi'],
        'Kitutu Chache South': ['Bogusero', 'Bogeka', 'Nyakoe', 'Kitutu Central', 'Nyatieko'],
        'Nyaribari Chache': ['Bobaracho', 'Kisii Central', 'Keumbu', 'Kiogoro', 'Birongo', 'Ibeno'],
        'Nyaribari Masaba': ['Ichuni', 'Nyamasibi', 'Masimba', 'Gesusu', 'Kiamokama'],
        'South Mugirango': ['Boikang\'a', 'Bogetenga', 'Borabu/Chimoroni', 'Moticho', 'Getenga']
    },
    'Kisumu': {
        'Kisumu Central': ['Railways', 'Migosi', 'Shaurimoyo Kaloleni', 'Market Milimani', 'Kondele', 'Nyalenda B'],
        'Kisumu East': ['Kajulu', 'Kolwa East', 'Manyatta B', 'Nyalenda A', 'Kolwa Central'],
        'Kisumu West': ['South West Kisumu', 'Central Kisumu', 'Kisumu North', 'West Kisumu', 'North West Kisumu'],
        'Muhoroni': ['Muhoroni/Koru', 'Miwani', 'Ombeyi', 'Masogo/Nyang\'oma', 'Chemelil/Chemase'],
        'Nyakach': ['South West Nyakach', 'North Nyakach', 'Central Nyakach', 'West Nyakach', 'South East Nyakach'],
        'Nyando': ['East Kano/Wawidhi', 'Awasi/Onjiko', 'Ahero', 'Kabonyo/Kanyagwal', 'Kobura'],
        'Seme': ['West Seme', 'Central Seme', 'East Seme', 'North Seme']
    },
    'Kitui': {
        'Kitui Central': ['Miambani', 'Township', 'Kyangwithya West', 'Mulango', 'Kyangwithya East'],
        'Kitui East': ['Zombe/Mwitika', 'Chuluni', 'Nzambani', 'Voo/Kyamatu', 'Endau/Malalani', 'Mutito/Kaliku'],
        'Kitui Rural': ['Kisasi', 'Mbitini', 'Kwavonza/Yatta', 'Kanyangi'],
        'Kitui South': ['Ikanga/Kyatune', 'Mutomo', 'Mutha', 'Ikutha', 'Kanziko', 'Athi'],
        'Kitui West': ['Mutonguni', 'Kauwi', 'Matinyani', 'Kwa Mutonga/Kithumula'],
        'Mwingi Central': ['Central', 'Kivou', 'Nguni', 'Nuu', 'Mui', 'Waita'],
        'Mwingi North': ['Ngomeni', 'Kyuso', 'Mumoni', 'Tseikuru', 'Tharaka'],
        'Mwingi West': ['Kyome/Thaana', 'Nguutani', 'Migwani', 'Kiomo/Kyethani']
    },
    'Kwale': {
        'Kinango': ['Ndavaya', 'Puma', 'Kinango', 'Mackinnon Road', 'Chengoni/Samburu', 'Mwavumbo', 'Kasemeni'],
        'Lunga Lunga': ['Pongwe/Kikoneni', 'Dzombo', 'Mwereni', 'Vanga'],
        'Matuga': ['Tsimba Golini', 'Waa', 'Tiwi', 'Kubo South', 'Mkongani'],
        'Msambweni': ['Gombato Bongwe', 'Ukunda', 'Kinondo', 'Ramisi']
    },
    'Laikipia': {
        'Laikipia East': ['Ngobit', 'Tigithi', 'Thingithu', 'Nanyuki', 'Umande'],
        'Laikipia North': ['Mukogodo West', 'Mukogodo East', 'Segera', 'Sosian'],
        'Laikipia West': ['Ol Moran', 'Rumuruti Township', 'Githiga', 'Marmanet', 'Igwamiti', 'Salama']
    },
    'Lamu': {
        'Lamu East': ['Faza', 'Kiunga', 'Basuba'],
        'Lamu West': ['Shella', 'Mkomani', 'Hindi', 'Mkunumbi', 'Hongwe', 'Witu', 'Bahari']
    },
    'Machakos': {
        'Kangundo': ['Kangundo North', 'Kangundo Central', 'Kangundo East', 'Kangundo West'],
        'Kathiani': ['Mitaboni', 'Kathiani Central', 'Upper Kaewa/Iveti', 'Lower Kaewa/Kaani'],
        'Machakos Town': ['Kalama', 'Mua', 'Mutituni', 'Machakos Central', 'Mumbuni North', 'Muvuti/Kiima Kimwe'],
        'Masinga': ['Kivaa', 'Masinga Central', 'Ekalakala', 'Muthesya', 'Ndithini'],
        'Matungulu': ['Tala', 'Matungulu North', 'Matungulu East', 'Matungulu West', 'Kyeleni'],
        'Mavoko': ['Athi River', 'Kinanie', 'Muthwani', 'Syokimau/Mulolongo'],
        'Mwala': ['Mbiuni', 'Makutano/Mwala', 'Masii', 'Muthetheni', 'Wamunyu', 'Kibauni'],
        'Yatta': ['Katangi', 'Ikombe', 'Ndalani', 'Matuu', 'Kithimani']
    },
    'Makueni': {
        'Kaiti': ['Ukia', 'Kee', 'Kilungu', 'Ilima'],
        'Kibwezi East': ['Masongaleni', 'Mtito Andei', 'Thange', 'Ivingoni/Nzambani'],
        'Kibwezi West': ['Makindu', 'Nguumo', 'Kikumbulyu North', 'Kikumbulyu South', 'Nguu/Masumba', 'Emali/Mulala'],
        'Kilome': ['Kasikeu', 'Mukaa', 'Kiima Kiu/Kalanzoni'],
        'Makueni': ['Wote', 'Muvau/Kikuumini', 'Mavindini', 'Kitise/Kithuki', 'Kathonzweni', 'Nzaui/Kilili/Kalamba', 'Mbitini'],
        'Mbooni': ['Tulimani', 'Mbooni', 'Kithungo/Kitundu', 'Kisau/Kiteta', 'Waia/Kako']
    },
    'Mandera': {
        'Banissa': ['Banissa', 'Derkhale', 'Guba', 'Malkamari', 'Kiliwehiri'],
        'Lafey': ['Alungu Gof', 'Lafey', 'Sala', 'Waranqara', 'Fino'],
        'Mandera East': ['Neboi', 'Township', 'Khalalio', 'Libehia', 'Arabia'],
        'Mandera North': ['Ashabito', 'Guticha', 'Morothile', 'Rhamu', 'Rhamu Dimtu'],
        'Mandera South': ['Wargudud', 'Kutulo', 'Elwak South', 'Elwak North', 'Shimbir Fatuma'],
        'Mandera West': ['Dandu', 'Takaba South', 'Takaba', 'Lagsure', 'Gither', 'Takaba North']
    },
    'Marsabit': {
        'Laisamis': ['Loiyangalani', 'Kargi/South Horr', 'Korr/Ngurunit', 'Logo Logo', 'Laisamis'],
        'Moyale': ['Butiye', 'Sololo', 'Heilu/Manyatta', 'Golbo', 'Moyale Township', 'Uran', 'Obbu'],
        'North Horr': ['Dukana', 'Maikona', 'North Horr', 'Turbi', 'Illeret'],
        'Saku': ['Sagante/Jaldesa', 'Karare', 'Marsabit Central', 'Marsabit Township']
    },
    'Meru': {
        'Buuri': ['Timau', 'Kisima', 'Kiirua/Naari', 'Ruiri/Rwarera', 'Kibirichia'],
        'Central Imenti': ['Mwanganthia', 'Abothuguchi Central', 'Abothuguchi West', 'Kiagu', 'Athiru Gaiti'],
        'Igembe Central': ['Kangeta', 'Njia', 'Igembe East', 'Athiru Ruujine', 'Akithi'],
        'Igembe North': ['Antuambui', 'Ntunene', 'Antubochiu', 'Naathu', 'Amwathi'],
        'Igembe South': ['Maua', 'Kiegoi/Antubetwe Kiongo', 'Athiru Gaiti', 'Akachiu', 'Kanuni'],
        'Imenti North': ['Municipality', 'Ntima East', 'Ntima West', 'Nyaki West', 'Nyaki East'],
        'Imenti South': ['Mitunguu', 'Igoji East', 'Igoji West', 'Abogeta East', 'Abogeta West', 'Nkuene'],
        'Tigania East': ['Thangatha', 'Mikinduri', 'Kiguchwa', 'Muthara', 'Karama'],
        'Tigania West': ['Athwana', 'Akithi', 'Kianjai', 'Nkomo', 'Mbeu']
    },
    'Migori': {
        'Awendo': ['North Kamagambo', 'Central Kamagambo', 'West Kamagambo', 'South Kamagambo'],
        'Kuria East': ['Gokeharaka/Getambwega', 'Ntimaru East', 'Ntimaru West', 'Nyabasi East', 'Nyabasi West'],
        'Kuria West': ['Bukira East', 'Bukira Central/Ikerege', 'Isibania', 'Makerero', 'Masaba', 'Tagare', 'Nyamosense/Komosoko'],
        'Nyatike': ['Kachieng', 'Kanyasa', 'North Kadem', 'Macalder/Kanyarwanda', 'Kaler', 'Got Kachola', 'Muhuru'],
        'Rongo': ['North Kamagambo', 'Central Sakwa', 'West Sakwa', 'South Sakwa'],
        'Suna East': ['God Jope', 'Suna Central', 'Kakrao', 'Kwa'],
        'Suna West': ['Wiga', 'Wasweta II', 'Ragana-Oruba', 'Wasimbete'],
        'Uriri': ['West Kanyamkago', 'North Kanyamkago', 'Central Kanyamkago', 'South Kanyamkago', 'East Kanyamkago']
    },
    'Mombasa': {
        'Changamwe': ['Port Reitz', 'Kipevu', 'Airport', 'Changamwe', 'Chaani'],
        'Jomvu': ['Jomvu Kuu', 'Magongo', 'Mikindani'],
        'Kisauni': ['Mjambere', 'Junda', 'Bamburi', 'Mwakirunge', 'Mtopanga', 'Magogoni', 'Shanzu'],
        'Likoni': ['Mtongwe', 'Shika Adabu', 'Bofu', 'Likoni', 'Timbwani'],
        'Mvita': ['Mji Wa Kale/Makadara', 'Tudor', 'Tononoka', 'Shimanzi/Ganjoni', 'Majengo'],
        'Nyali': ['Frere Town', 'Ziwa la Ng\'ombe', 'Mkomani', 'Kongowea', 'Kadzandani']
    },
    'Murang\'a': {
        'Gatanga': ['Ithanga', 'Kakuzi/Mitubiri', 'Mugumo-ini', 'Kihumbu-ini', 'Gatanga', 'Kariara'],
        'Kahuro': ['Murarandia', 'Gaturi', 'Ruchu', 'Kamacharia', 'Wangu', 'Mugoiri'],
        'Kandara': ['Ng\'araria', 'Muruka', 'Kagundu-ini', 'Gaichanjiru', 'Ithiru', 'Ruchu'],
        'Kangema': ['Kanyenya-ini', 'Muguru', 'Rwathia', 'Irati'],
        'Kigumo': ['Kangari', 'Kigumo', 'Muthithi', 'Kinyona', 'Kirimiri'],
        'Kiharu': ['Wangu', 'Mugoiri', 'Mbiri', 'Township', 'Murarandia', 'Gaturi'],
        'Maragwa': ['Kimorori/Wempa', 'Makuyu', 'Kambiti', 'Kamahuha', 'Ichagaki', 'Nginda'],
        'Mathioya': ['Kamacharia', 'Gitugi', 'Kiru', 'Kiriani', 'Kihumbu-ini']
    },
    'Nairobi': {
        'Dagoretti North': ['Kilimani', 'Kawangware', 'Gatina', 'Kileleshwa', 'Kabiro'],
        'Dagoretti South': ['Mutu-ini', 'Ngando', 'Riruta', 'Uthiru/Ruthimitu', 'Waithaka'],
        'Embakasi Central': ['Kayole North', 'Kayole Central', 'Kayole South', 'Komarock', 'Matopeni/Spring Valley'],
        'Embakasi East': ['Upper Savanna', 'Lower Savanna', 'Embakasi', 'Utawala', 'Mihango'],
        'Embakasi North': ['Kariobangi North', 'Dandora Area I', 'Dandora Area II', 'Dandora Area III', 'Dandora Area IV'],
        'Embakasi South': ['Imara Daima', 'Kwa Njenga', 'Kwa Reuben', 'Pipeline', 'Kware'],
        'Embakasi West': ['Umoja I', 'Umoja II', 'Mowlem', 'Kariobangi South'],
        'Kamukunji': ['Pumwani', 'Eastleigh North', 'Eastleigh South', 'Airbase', 'California'],
        'Kasarani': ['Clay City', 'Mwiki', 'Kasarani', 'Njiru', 'Ruai'],
        'Kibra': ['Laini Saba', 'Lindi', 'Makina', 'Woodley/Kenyatta Golf Course', 'Sarangombe'],
        'Langata': ['Karen', 'Nairobi West', 'Mugumo-ini', 'South C', 'Nyayo Highrise'],
        'Makadara': ['Maringo/Hamza', 'Viwandani', 'Harambee', 'Makongeni'],
        'Mathare': ['Hospital', 'Mabatini', 'Huruma', 'Ngei', 'Mlango Kubwa', 'Kiamaiko'],
        'Roysambu': ['Githurai', 'Kahawa West', 'Zimmerman', 'Roysambu', 'Kahawa'],
        'Ruaraka': ['Babadogo', 'Utalii', 'Mathare North', 'Lucky Summer', 'Korogocho'],
        'Starehe': ['Nairobi Central', 'Ngara', 'Pangani', 'Ziwani/Kariokor', 'Landimawe', 'Nairobi South'],
        'Westlands': ['Kitisuru', 'Parklands/Highridge', 'Karura', 'Kangemi', 'Mountain View']
    },
    'Nakuru': {
        'Bahati': ['Bahati', 'Kiamaina', 'Lanet/Umoja', 'Kabatini', 'Dundori'],
        'Gilgil': ['Gilgil', 'Elementaita', 'Mbaruk/Eburu', 'Malewa West', 'Murindati'],
        'Kuresoi North': ['Kiptororo', 'Nyota', 'Sirikwa', 'Kamara', 'Tinet'],
        'Kuresoi South': ['Keringet', 'Kiptagich', 'Tinet', 'Amalo', 'Olenguruone'],
        'Molo': ['Mariashoni', 'Elburgon', 'Turi', 'Molo'],
        'Naivasha': ['Biashara', 'Hells Gate', 'Lake View', 'Mai Mahiu', 'Maiella', 'Olkaria', 'Naivasha East', 'Viwandani'],
        'Nakuru Town East': ['Kivumbini', 'Flamingo', 'Nakuru East', 'Menengai', 'Biashara'],
        'Nakuru Town West': ['Rhoda', 'London', 'Kaptembwo', 'Kapkures', 'Barut'],
        'Njoro': ['Mau Narok', 'Mauche', 'Kihingo', 'Nessuit', 'Lare', 'Njoro'],
        'Rongai': ['Menengai West', 'Soin', 'Visoi', 'Mosop', 'Solai'],
        'Subukia': ['Subukia', 'Waseges', 'Kabazi']
    },
    'Nandi': {
        'Aldai': ['Kaptumo-Kaboi', 'Koyo-Ndurio', 'Kemeloi-Maraba', 'Kobujoi', 'Terik'],
        'Chesumei': ['Chemundu/Kapng\'etuny', 'Kosirai', 'Kiptumo', 'Lelmokwo/Ngechek', 'Kabiyet'],
        'Emgwen': ['Kaptel/Kamoiywo', 'Chepkumia', 'Kapsabet', 'Kilibwoni'],
        'Mosop': ['Kipkaren', 'Kurgung/Surungai', 'Kabiemit', 'Ndalat', 'Kabisaga', 'Sangalo/Kebulonik'],
        'Nandi Hills': ['Nandi Hills', 'Chepkunyuk', 'Ollessos', 'Kapchorua'],
        'Tinderet': ['Songhor/Soba', 'Tindiret', 'Chemelil/Chemase', 'Kapsimotwo']
    },
    'Narok': {
        'Emurua Dikirr': ['Ilkerin', 'Mogondo', 'Kapsasian'],
        'Kilgoris': ['Kilgoris Central', 'Keyian', 'Angata Barikoi', 'Shankoe', 'Kimintet', 'Lolgorian'],
        'Narok East': ['Mosiro', 'Ildamat', 'Keekonyokie', 'Suswa'],
        'Narok North': ['Olokurto', 'Narok Town', 'Nkareta', 'Olorropil', 'Melili', 'Olpusimoru'],
        'Narok South': ['Majimoto/Naroosura', 'Ololulung\'a', 'Melelo', 'Loita', 'Sogoo', 'Sagamian'],
        'Narok West': ['Ilmotiok', 'Mara', 'Siana', 'Naikarra']
    },
    'Nyamira': {
        'Borabu': ['Mekenene', 'Kiabonyoru', 'Nyansiongo', 'Esise'],
        'Kitutu Masaba': ['Rigoma', 'Gachuba', 'Kemera', 'Magombo', 'Manga'],
        'Masaba North': ['Gesima', 'Kemera', 'Magombo', 'Manga', 'Rigoma', 'Gachuba'],
        'North Mugirango': ['Itibo', 'Bomwagamo', 'Bokeira', 'Magwagwa', 'Ekerenyo'],
        'West Mugirango': ['Nyamaiya', 'Bogichora', 'Bosamaro', 'Bonyamatuta', 'Township']
    },
    'Nyandarua': {
        'Kinangop': ['Engineer', 'Gathara', 'North Kinangop', 'Murungaru', 'Njabini/Kiburu', 'Nyakio', 'Githabai', 'Magumu'],
        'Kipipiri': ['Wanjohi', 'Kipipiri', 'Geta', 'Githioro'],
        'Ndaragwa': ['Shamata', 'Ndaragwa Central', 'Kiriita', 'Leshau/Pondo'],
        'Ol Jorok': ['Kaimbaga', 'Gathanji', 'Gatimu', 'Weru', 'Charagita'],
        'Ol Kalou': ['Kanjuiri Range', 'Mirangine', 'Karau', 'Kaimbaga', 'Rurii']
    },
    'Nyeri': {
        'Kieni': ['Naromoru/Kiamathaga', 'Kabaru', 'Gakawa', 'Rugi', 'Mweiga', 'Mwiyogo/Endarasha'],
        'Mathira': ['Karatina Town', 'Kirimukuyu', 'Iriaini', 'Konyu', 'Magutu', 'Ruguru'],
        'Mukurweini': ['Gikondi', 'Rugi', 'Mukurwe-ini West', 'Mukurwe-ini Central'],
        'Nyeri Town': ['Kamakwa/Mukaro', 'Rware', 'Gatitu/Muruguru', 'Ruring\'u', 'Kiganjo/Mathari'],
        'Othaya': ['Mahiga', 'Iria-ini', 'Chinga', 'Karima', 'Giakanja'],
        'Tetu': ['Dedan Kimathi', 'Wamagana', 'Aguthi-Gaaki', 'Kirimari']
    },
    'Samburu': {
        'Samburu East': ['Wamba East', 'Wamba West', 'Wamba North', 'Waso'],
        'Samburu North': ['El Barta', 'Nachola', 'Ndoto', 'Nyiro', 'Angata Nanyokie', 'Baawa'],
        'Samburu West': ['Lodokejek', 'Suguta Marmar', 'Maralal', 'Loosuk', 'Poro']
    },
    'Siaya': {
        'Alego Usonga': ['Usonga', 'West Alego', 'Central Alego', 'Siaya Township', 'North Alego', 'South East Alego'],
        'Bondo': ['West Yimbo', 'Central Sakwa', 'South Sakwa', 'Yimbo East', 'West Sakwa', 'North Sakwa'],
        'Gem': ['North Gem', 'West Gem', 'Central Gem', 'Yala Township', 'South Gem', 'East Gem'],
        'Rarieda': ['East Asembo', 'West Asembo', 'North Uyoma', 'South Uyoma', 'West Uyoma'],
        'Ugenya': ['West Ugenya', 'Ukwala', 'North Ugenya', 'East Ugenya'],
        'Ugunja': ['Sidindi', 'Sigomere', 'Ugunja']
    },
    'Taita-Taveta': {
        'Mwatate': ['Wundanyi', 'Werugha', 'Wumingu/Kishushe', 'Mwatate', 'Bura'],
        'Taveta': ['Chala', 'Mahoo', 'Bomani', 'Mboghoni', 'Mata'],
        'Voi': ['Mbololo', 'Sagalla', 'Kaloleni', 'Maungu', 'Ngolia', 'Kasigau', 'Marungu'],
        'Wundanyi': ['Wundanyi/Mbale', 'Werugha', 'Wumingu/Kishushe']
    },
    'Tana River': {
        'Bura': ['Chewele', 'Bura', 'Bangale', 'Sala', 'Madogo'],
        'Galole': ['Wayu', 'Hola', 'Kipini East', 'Kipini West'],
        'Garsen': ['Kipini East', 'Garsen South', 'Kipini West', 'Garsen Central', 'Garsen North', 'Garsen West']
    },
    'Tharaka-Nithi': {
        'Chuka/Igambang\'ombe': ['Mariani', 'Karingani', 'Magumoni', 'Igambang\'ombe', 'Mugwe'],
        'Maara': ['Mitheru', 'Muthambi', 'Mwimbi', 'Ganga', 'Chogoria'],
        'Tharaka': ['Gatunga', 'Mukothima', 'Nkondi', 'Chiakariga', 'Marimanti']
    },
    'Trans Nzoia': {
        'Cherangany': ['Sinyerere', 'Makutano', 'Kaplamai', 'Motosiet', 'Cherangany/Suwerwa', 'Chepsiro/Kiptoror', 'Sitatunga'],
        'Endebess': ['Endebess', 'Chepchoina', 'Matumbei'],
        'Kiminini': ['Kiminini', 'Waitaluk', 'Sirende', 'Hospital', 'Sikhendu', 'Nabiswa'],
        'Kwanza': ['Kapomboi', 'Kwanza', 'Keiyo', 'Bidii'],
        'Saboti': ['Kinyoro', 'Matisi', 'Tuwani', 'Saboti', 'Machewa']
    },
    'Turkana': {
        'Loima': ['Kotaruk/Lobei', 'Turkwel', 'Loima', 'Lokiriama/Lorengippi'],
        'Turkana Central': ['Kerio Delta', 'Kang\'atotha', 'Kalokol', 'Lodwar Township', 'Kanamkemer'],
        'Turkana East': ['Lokori/Kochodin', 'Katilu', 'Kaputir'],
        'Turkana North': ['Kaaleng/Kaikor', 'Kibish', 'Lakezone', 'Nakalale'],
        'Turkana South': ['Kalapata', 'Lobokat', 'Kaputir', 'Lokichar', 'Lolomarik'],
        'Turkana West': ['Kakuma', 'Lopur', 'Letea', 'Songot', 'Kalobeyei', 'Lokichoggio', 'Nanaam']
    },
    'Uasin Gishu': {
        'Ainabkoi': ['Kapsoya', 'Kaptagat', 'Ainabkoi/Olare'],
        'Kapseret': ['Simat/Kapseret', 'Kipkenyo', 'Ngeria', 'Megun', 'Langas'],
        'Kesses': ['Racecourse', 'Cheptiret/Kipchamo', 'Tulwet/Chuiyat', 'Tarakwa'],
        'Moiben': ['Tembelio', 'Sergoit', 'Karuna/Meibeki', 'Moiben', 'Kimumu'],
        'Soy': ['Moi\'s Bridge', 'Kapkures', 'Ziwa', 'Segero/Barsombe', 'Kipsomba', 'Soy', 'Kuinet/Kapsuswa'],
        'Turbo': ['Ngenyilel', 'Tapsagoi', 'Kamagut', 'Kiplombe', 'Huruma']
    },
    'Vihiga': {
        'Emuhaya': ['North East Bunyore', 'Central Bunyore', ' West Bunyore'],
        'Hamisi': ['Shiru', 'Gisambai', 'Shamakhokho', 'Banja', 'Muhudu', 'Tambua', 'Jepkoyai'],
        'Luanda': ['Luanda Township', 'Wemilabi', 'Mwibona', 'Luanda South', 'Emabungo'],
        'Sabatia': ['Lyaduywa/Izava', 'West Sabatia', 'Chavakali', 'North Maragoli', 'Wodanga', 'Busali'],
        'Vihiga': ['Lugaga-Wamuluma', 'South Maragoli', 'Central Maragoli', 'Mungoma']
    },
    'Wajir': {
        'Eldas': ['Eldas', 'Della', 'Lakoley South/Basir', 'Elnur/Tula', 'Benane'],
        'Tarbaj': ['Elben', 'Sarman', 'Tarbaj', 'Wargadud'],
        'Wajir East': ['Godoma', 'Wagberi', 'Township', 'Barwago', 'Khorof/Harar'],
        'Wajir North': ['Danaba', 'Bute', 'Korondille', 'Malkagufu', 'Gurar', 'Batalu'],
        'Wajir South': ['Benane', 'Burder', 'Dadajabula', 'Habaswein', 'Lagboghol South', 'Ibrahim Ure'],
        'Wajir West': ['Arbajahan', 'Hadado/Athibohol', 'Ademasajide', 'Ganyure/Wagalla', 'Eldas']
    },
    'West Pokot': {
        'Kapenguria': ['Riwo', 'Kapenguria', 'Mnagei', 'Siyoi', 'Endugh', 'Sook'],
        'Kacheliba': ['Suam', 'Kodich', 'Kasei', 'Kapchok', 'Kiwawa', 'Alale'],
        'Pokot South': ['Chepareria', 'Batei', 'Lelan', 'Tapach'],
        'Sigor': ['Weiwei', 'Masool', 'Lomut', 'Sekerr', 'Marich']
    }
}
