from django.db import models
from django.contrib.auth.models import User
import uuid

LANGUAGES = [("ab","Abkhazian"),
("aa","Afar"),
("af","Afrikaans"),
("ak","Akan"),
("sq","Albanian"),
("am","Amharic"),
("ar","Arabic"),
("an","Aragonese"),
("hy","Armenian"),
("as","Assamese"),
("av","Avaric"),
("ae","Avestan"),
("ay","Aymara"),
("az","Azerbaijani"),
("bm","Bambara"),
("ba","Bashkir"),
("eu","Basque"),
("be","Belarusian"),
("bn","Bengali"),
("bi","Bislama"),
("bs","Bosnian"),
("br","Breton"),
("bg","Bulgarian"),
("my","Burmese"),
("ca","Catalan"),
("ch","Chamorro"),
("ce","Chechen"),
("ny","Chichewa"),
("zh","Chinese"),
("cv","Chuvash"),
("kw","Cornish"),
("co","Corsican"),
("cr","Cree"),
("hr","Croatian"),
("cs","Czech"),
("da","Danish"),
("dv","Divehi"),
("nl","Dutch"),
("dz","Dzongkha"),
("en","English"),
("eo","Esperanto"),
("et","Estonian"),
("ee","Ewe"),
("fo","Faroese"),
("fj","Fijian"),
("fi","Finnish"),
("fr","French"),
("fy West","Western Frisian"),
("ff","Fulah"),
("gd","Gaelic"),
("gl","Galician"),
("lg","Ganda"),
("ka","Georgian"),
("de","German"),
("el","Greek"),
("kl","Kalaallisut"),
("gn","Guarani"),
("gu","Gujarati"),
("ht","Haitian"),
("ha","Hausa"),
("he","Hebrew"),
("hz","Herero"),
("hi","Hindi"),
("hu","Hungarian"),
("is","Icelandic"),
("io","Ido"),
("ig","Igbo"),
("id","Indonesian"),
("iu","Inuktitut"),
("ik","Inupiaq"),
("ga","Irish"),
("it","Italian"),
("ja","Japanese"),
("jv","Javanese"),
("kn","Kannada"),
("kr","Kanuri"),
("ks","Kashmiri"),
("kk","Kazakh"),
("ki","Kikuyu"),
("rw","Kinyarwanda"),
("ky","Kirghiz"),
("kv","Komi"),
("kg","Kongo"),
("ko","Korean"),
("kj","Kuanyama"),
("ku","Kurdish"),
("lo","Lao"),
("la","Latin"),
("lv","Latvian"),
("li","Limburgan"),
("ln","Lingala"),
("lt","Lithuanian"),
("lb","Luxembourgish"),
("mk","Macedonian"),
("mg","Malagasy"),
("ms","Malay"),
("ml","Malayalam"),
("mt","Maltese"),
("gv","Manx"),
("mi","Maori"),
("mr","Marathi"),
("mh","Marshallese"),
("mn","Mongolian"),
("na","Nauru"),
("nv","Navajo"),
("nd North","North Ndebele"),
("nr South","South Ndebele"),
("ng","Ndonga"),
("ne","Nepali"),
("no","Norwegian"),
("oc","Occitan"),
("oj","Ojibwa"),
("or","Oriya"),
("om","Oromo"),
("os","Ossetian"),
("pi","Pali"),
("ps","Pashto"),
("fa","Persian"),
("pl","Polish"),
("pt","Portuguese"),
("pa","Punjabi"),
("qu","Quechua"),
("ro","Romanian"),
("rm","Romansh"),
("rn","Rundi"),
("ru","Russian"),
("se","Sami"),
("sm","Samoan"),
("sg","Sango"),
("sa","Sanskrit"),
("sc","Sardinian"),
("sr","Serbian"),
("sn","Shona"),
("sd","Sindhi"),
("si","Sinhala"),
("sk","Slovak"),
("sl","Slovenian"),
("so","Somali"),
("st","Southern Sotho"),
("es","Spanish"),
("su","Sundanese"),
("sw","Swahili"),
("ss","Swati"),
("sv","Swedish"),
("tl","Tagalog"),
("ty","Tahitian"),
("tg","Tajik"),
("ta","Tamil"),
("tt","Tatar"),
("te","Telugu"),
("th","Thai"),
("bo","Tibetan"),
("ti","Tigrinya"),
("to","Tonga"),
("ts","Tsonga"),
("tn","Tswana"),
("tr","Turkish"),
("tk","Turkmen"),
("tw","Twi"),
("ug","Uighur"),
("uk","Ukrainian"),
("ur","Urdu"),
("uz","Uzbek"),
("ve","Venda"),
("vi","Vietnamese"),
("vo","Volapük"),
("wa","Walloon"),
("cy","Welsh"),
("wo","Wolof"),
("xh","Xhosa"),
("yi","Yiddish"),
("yo","Yoruba"),
("za","Zhuang"),
("zu","Zulu"),
]

class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    image       = models.ImageField(default='media/default.jpg', upload_to='media/profile_picks')
    status      = models.CharField(max_length=70, null=True, choices=(('Admin', 'Admin'), ('Actor', 'Actor'), ('Viewer', 'Viewer'), ('NLD', 'NLD')), default='NLD' )
    gender      = models.CharField(max_length=70, null=True, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), default='Other')
    age         = models.IntegerField(default=0)
    healthcare  = models.CharField(max_length=70, null=True, choices=(('Psychologist', 'Psychologist'), ('Psychatrist', 'Psychatrist'), ('Other physician', 'Other physician'), ('Actor', 'Actor'), ('Other', 'Other')))
    institute   = models.CharField(max_length=70, null=True, default='Not Specified')
    experience  = models.IntegerField(default=0)
    # languages_spoken = models.CharField(choices=LANGUAGES, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} Profile"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
        
    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)
