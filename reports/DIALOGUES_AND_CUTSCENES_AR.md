# السجل الكامل لترجمة المشاهد السينمائية والحوارات — Crash Bandicoot N. Sane Trilogy

## ملخص الحالة والتغطية

- **المشاهد السينمائية المحقونة داخل اللعبة (`update.pak`)**: **14 مشهدًا ناطقًا** من أصل **15 مشهدًا** (إجمالي **96 لوحة ترجمة نصية** موزعة بدقة على **44 لقطة `_ui.igz`**).
- **المشهد الصامت**: `Crash1_Outro_Cinematic` صامت بالكامل (`0` أحداث حوار صوتي) ولا يتطلب ترجمة.
- **الحوارات الصوتية `_LOC_` المستخرجة والمترجمة (48 مقطعًا)**: تشمل **35 حوارًا لرؤوس المحادثة (`TalkingHeads`)** في غرف الانتقال لكراش 2 وكراش 3 + **13 سطرًا لشاشات العنوان والزعماء داخل المعارك**.
  - *ملاحظة تقنية حول `TalkingHeads`*: تختلف حوارات رؤوس المحادثة داخل غرف الانتقال (`L200_Hub` و`L300_Hub`) عن المشاهد السينمائية لأنها تُستدعى برمجيًا عبر عقد `VSC` ولا يمتلك محرك اللعبة نداء `CGuiEventSubtitlesShow` متصلًا بالـ VSC في النسخة الأصلية؛ ونظرًا لعدم توفر تشغيل فعلي لـ Steam أثناء البناء لاختبار حقن بايتكود `VSC` في الميدان، تم الحفاظ على سلامة الـ Hubs من التلف، وإتاحة النص المترجم الكامل للجميع في هذا السجل وملفات البيانات إلى أن يتاح اختبار VSC حيًا.

---

## القسم الأول: المشاهد السينمائية المفعّلة داخل اللعبة (`14` مشهدًا ناطقًا)

### 1. مقدمة شعار Vicarious Visions (`VV_Logo_Intro.pak` — Shared)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_VV_01` | `0.05s–2.75s` | د. نيو كورتكس | Developed by Vicarious Visions. | من تطوير فيكاريوس فيجنز! |
| `Sub_VV_02` | `8.12s–10.32s` | د. نيو كورتكس | It's Crash Bandicoot! | إنه كراش بانديكوت! |

### 2. المشهد الافتتاحي - كراش بانديكوت 1 (`Crash1_Intro_Cinematic.pak` — Crash 1)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C1_Intro_01` | `1.65s–8.35s` | د. نيتروس بريو | But Dr. Cortex, we haven't determined the cause of past failures! | ولكن يا دكتور كورتكس، / لم نحدد سبب الإخفاقات السابقة بعد! |
| `Sub_C1_Intro_02` | `8.85s–11.40s` | د. نيو كورتكس | Moron! This bandicoot will be my general, | أحمق! سيكون هذا البانديكوت قائدي، |
| `Sub_C1_Intro_03` | `11.50s–16.05s` | د. نيو كورتكس | and he will lead my Cortex Commandos to world domination! | وسيقود كوماندوز كورتكس / نحو السيطرة على العالم! |
| `Sub_C1_Intro_04` | `16.65s–20.15s` | د. نيو كورتكس | This time, I shall reign triumphant! | هذه المرة، سأحقق النصر المبين! |
| `Sub_C1_Intro_05` | `25.70s–30.65s` | د. نيو كورتكس | We are closer than ever before! Quickly! Into the Vortex! | إننا أقرب من أي وقت مضى! / أسرع! إلى الدوامة! |
| `Sub_C1_Intro_06` | `31.35s–35.42s` | د. نيتروس بريو | But Dr. Cortex, the Vortex is not ready! | ولكن يا دكتور كورتكس، الدوامة ليست جاهزة! |
| `Sub_C1_Intro_07` | `35.50s–40.00s` | د. نيتروس بريو | We have no idea what it could do! | ليست لدينا أي فكرة عما قد تفعله! |
| `Sub_C1_Intro_08` | `47.80s–49.40s` | د. نيو كورتكس | Failure again! | فشل مجددا! |
| `Sub_C1_Intro_09` | `53.15s–54.45s` | د. نيو كورتكس | Capture him! | أمسكوا به! |
| `Sub_C1_Intro_10` | `56.50s–57.70s` | كراش بانديكوت | Uh-oh! | أوه، لا! |
| `Sub_C1_Intro_11` | `60.20s–63.30s` | د. نيو كورتكس | Prepare the female bandicoot! | جهزوا أنثى البانديكوت! |

### 3. مشهد هزيمة كورتكس (النهاية العادية) - كراش 1 (`Crash1_Boss_Outro_Cinematic.pak` — Crash 1)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C1_BossOut_01` | `0.20s–2.95s` | د. نيو كورتكس | Aaaah! | آااااااه! |
| `Sub_C1_BossOut_02` | `3.08s–6.23s` | د. نيو كورتكس | Aaaaah! | آااااااه! |

### 4. المشهد الافتتاحي - كراش بانديكوت 2 (`Crash2_Intro_Cinematic.pak` — Crash 2)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C2_Intro_01` | `0.51s–6.51s` | د. نيو كورتكس | Aaaah! | آااااااه! |
| `Sub_C2_Intro_02` | `21.23s–24.58s` | د. نيو كورتكس | Crystals... Of course! | البلورات... بالطبع! |
| `Sub_C2_Intro_03` | `25.44s–26.39s` | د. إن جين | No! | لا! |
| `Sub_C2_Intro_04` | `33.21s–38.01s` | د. إن جين | But Dr. Cortex, to reach full power, | ولكن يا دكتور كورتكس، لبلوغ الطاقة القصوى، |
| `Sub_C2_Intro_05` | `38.07s–40.87s` | د. إن جين | we need not only your Master Crystal, | لا نحتاج إلى بلورتك الرئيسية وحدها، |
| `Sub_C2_Intro_06` | `40.95s–46.30s` | د. إن جين | but also the remaining 25 Slave Crystals from the surface. | بل إلى البلورات الـ25 التابعة / المتبقية على سطح الأرض أيضا. |
| `Sub_C2_Intro_07` | `46.59s–50.29s` | د. إن جين | How do you expect to retrieve them | كيف تتوقع منا استعادتها |
| `Sub_C2_Intro_08` | `50.40s–53.55s` | د. إن جين | when we don't have any Earth-bound operatives left? | ولم يتبق لنا أي عملاء على الأرض؟! |
| `Sub_C2_Intro_09` | `55.11s–57.71s` | د. نيو كورتكس | You fool! Do you think I'm unaware of the situation? | أيها الأحمق! أتظنني غافلا عن الموقف؟ |
| `Sub_C2_Intro_10` | `58.56s–61.91s` | د. نيو كورتكس | If we don't have any friends left on the surface, | إن لم يتبق لنا أي أصدقاء على السطح، |
| `Sub_C2_Intro_11` | `62.73s–66.68s` | د. نيو كورتكس | then we'll need to find... an enemy! | فسنضطر حينها للعثور على... عدو! |
| `Sub_C2_Intro_12` | `73.44s–74.84s` | كوكو بانديكوت | Crash! Crash! | كراش! كراش! |
| `Sub_C2_Intro_13` | `74.92s–76.37s` | كوكو بانديكوت | CRASH! | كرااااش! |
| `Sub_C2_Intro_14` | `76.68s–80.23s` | كوكو بانديكوت | My battery is fried! Make yourself useful, big brother, and bring an extra battery for me! | بطاريتي احترقت! أرني فائدتك يا أخي الأكبر / وأحضر لي بطارية إضافية! |

### 5. مشهد النهاية العادية - كراش بانديكوت 2 (`Crash2_Outro_Cinematic.pak` — Crash 2)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C2_Outro_01` | `2.49s–7.79s` | كوكو بانديكوت | Crash, what do you think happened to Cortex? And the Cortex Vortex? | كراش، ما الذي تظنه حدث لكورتكس؟ / وماذا عن دوامة كورتكس؟ |
| `Sub_C2_Outro_02` | `8.16s–9.66s` | كوكو بانديكوت | It's still up there. | لا تزال هناك في الأعلى. |

### 6. مشهد نهاية 100% (تدمير الدوامة) - كراش 2 (`Crash2_Outro100_Cinematic.pak` — Crash 2)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C2_Out100_01` | `4.02s–6.77s` | د. نيتروس بريو | We're ready, Crash. | نحن مستعدون يا كراش. |
| `Sub_C2_Out100_02` | `7.17s–11.97s` | د. نيتروس بريو | Would you like to do the... honors? | أتود أن تتولى أنت... شرف التنفيذ؟ |

### 7. المشهد الافتتاحي - كراش بانديكوت 3 (`Crash3_Intro_Cinematic.pak` — Crash 3)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_Intro_01` | `16.68s–19.43s` | أوكا أوكا | Free at last! | حر طليق أخيرا! |
| `Sub_C3_Intro_02` | `31.86s–37.21s` | أكو أكو | Uka Uka is free? No, it cannot be! | أوكا أوكا طليق؟ لا، لا يعقل هذا! |
| `Sub_C3_Intro_03` | `37.96s–41.41s` | أكو أكو | Evil... great evil has come! | الشر... شر عظيم قد حل! |
| `Sub_C3_Intro_04` | `48.60s–53.95s` | أوكا أوكا | Nobody dares fail the great Uka Uka, not even once! | لم يجرؤ أحد قط على خذلان / أوكا أوكا العظيم ولو مرة! |
| `Sub_C3_Intro_05` | `54.09s–59.19s` | أوكا أوكا | Yet you, Cortex... you have failed me twice! | ولكنك يا كورتكس... / لقد خذلتني مرتين! |
| `Sub_C3_Intro_06` | `61.29s–64.14s` | د. نيو كورتكس | Oh, Great Uka Uka, it was that wretched bandicoot! | يا أوكا أوكا العظيم، / كان ذلك البانديكوت اللعين! |
| `Sub_C3_Intro_07` | `65.35s–71.85s` | أوكا أوكا | From deep inside my temple prison, I sent you the simplest of instructions to follow. | من أعماق سجني في المعبد، / أرسلت إليك أبسط التعليمات لتنفيذها. |
| `Sub_C3_Intro_08` | `72.30s–76.70s` | أوكا أوكا | Yet you lost the gems! You lost the crystals! | لكنك خسرت الجواهر! وخسرت البلورات! |
| `Sub_C3_Intro_09` | `76.83s–79.88s` | أوكا أوكا | And I have lost my patience! | وأنا فقدت صبري! |
| `Sub_C3_Intro_10` | `80.40s–86.60s` | أوكا أوكا | Now there is no other source of energy left on this planet! | لم يعد هناك الآن أي مصدر طاقة آخر / متبق على هذا الكوكب! |
| `Sub_C3_Intro_11` | `86.85s–90.15s` | د. نيو كورتكس | I know we've had some... unfortunate setbacks... | أعلم أننا مررنا ببعض... الانتكاسات المؤسفة... |
| `Sub_C3_Intro_12` | `90.38s–91.98s` | أوكا أوكا | You failed! | وفشلت! |
| `Sub_C3_Intro_13` | `92.31s–96.31s` | أوكا أوكا | However, because your bumbling managed to set me free, | ولكن بما أن تخبطك الأخرق / قد نجح في تحريري، |
| `Sub_C3_Intro_14` | `96.50s–99.85s` | أوكا أوكا | I am feeling generous today. | فإنني أشعر بالكرم اليوم. |
| `Sub_C3_Intro_15` | `100.50s–104.05s` | أوكا أوكا | There is still a way to gather the energy needed | لا تزال هناك وسيلة لحشد القوة اللازمة |
| `Sub_C3_Intro_16` | `104.28s–107.28s` | أوكا أوكا | to enslave this pitiful planet! | لاستعباد هذا الكوكب البائس! |
| `Sub_C3_Intro_17` | `107.61s–115.96s` | أوكا أوكا | And this time, this time, the great Uka Uka will make sure you do it right! | وهذه المرة، هذه المرة بالذات، / سيضمن أوكا أوكا العظيم أن تنجز الأمر بإتقان! |
| `Sub_C3_Intro_18` | `120.18s–124.63s` | أكو أكو | After many eons, my evil twin brother, | بعد دهور طويلة، تحرر أخي التوأم الشرير، |
| `Sub_C3_Intro_19` | `124.74s–128.94s` | أكو أكو | Uka Uka, has been freed from his underground prison. | أوكا أوكا، من سجنه تحت الأرض. |
| `Sub_C3_Intro_20` | `129.63s–135.08s` | أكو أكو | I locked him there long ago to protect the world from his malice. | لقد حبسته هناك منذ زمن بعيد / لحماية العالم من شره وحقده. |
| `Sub_C3_Intro_21` | `135.81s–141.46s` | أكو أكو | Now that he is free again, he must be stopped! | والآن، وقد أصبح حرا مجددا، / لا بد من إيقافه! |
| `Sub_C3_Intro_22` | `148.59s–149.84s` | أكو أكو | Children! | يا أبنائي! |
| `Sub_C3_Intro_23` | `150.03s–154.18s` | أكو أكو | Uka Uka and Cortex plan on using this Time-Twister machine | يخطط أوكا أوكا وكورتكس لاستخدام آلة ثني الزمن هذه |
| `Sub_C3_Intro_24` | `154.32s–158.12s` | أكو أكو | to gather the crystals that lay scattered across time! | لجمع البلورات المتناثرة عبر العصور! |
| `Sub_C3_Intro_25` | `158.55s–161.90s` | أكو أكو | I have brought you here to recover the crystals before them. | لقد أحضرتكما إلى هنا / لاستعادة البلورات قبلهما. |
| `Sub_C3_Intro_26` | `162.48s–167.93s` | أكو أكو | To open a time portal, simply stand upon a button, and then jump into the portal. | لفتح بوابة الزمن، قفا فوق الزر ببساطة / ثم اقفزا داخل البوابة. |
| `Sub_C3_Intro_27` | `168.66s–170.16s` | أكو أكو | Good luck! | حظا موفقا! |

### 8. حوار كورتكس في الغرفة الثانية (بعد تايني) - كراش 3 (`C3_Hub_02_Intro.pak` — Crash 3 Hub)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_Hub02_01` | `1.35s–7.60s` | د. نيو كورتكس | Why? Why do you insist on being such a thorn in our sides?! | لماذا؟ لماذا تصرون على البقاء / شوكة في خاصرتنا؟! |
| `Sub_C3_Hub02_02` | `8.24s–10.24s` | د. نيو كورتكس | Who? What? Where was I? | من؟ ماذا؟ أين كنت؟ |
| `Sub_C3_Hub02_03` | `10.92s–15.92s` | د. نيو كورتكس | Oh... Tiny was a good fellow. He hated everyone and everything, but he had a good heart nonetheless. | آه... كان تايني رفيقا طيبا، / كره الجميع وكل شيء، لكن قلبه كان طيبا. |
| `Sub_C3_Hub02_04` | `16.68s–22.56s` | د. نيو كورتكس | Please try to be a little more considerate of my minions next time. | أرجو أن تكونوا أكثر تعقلا / مع أتباعي في المرة القادمة. |

### 9. تهكم كورتكس الثاني في غرفة الزمن - كراش 3 (`C3_Cortex_Taunt_2.pak` — Crash 3 Hub)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_Taunt2_01` | `1.35s–4.95s` | د. نيو كورتكس | Alright, you've foiled a few plans before, | حسنا، لقد أفسدت بضع خطط لنا من قبل، |
| `Sub_C3_Taunt2_02` | `5.20s–8.20s` | د. نيو كورتكس | but I never expected you to make it this far. | لكنني لم أتوقع أبدا أن تصلوا إلى هذا الحد. |
| `Sub_C3_Taunt2_03` | `8.64s–17.64s` | د. نيو كورتكس | If you don't turn back now, I'll make sure you and the rest of the universe suffer for a thousand years! | إن لم تعودوا أدراجكم، فسأذيقكم / والكون بأسره ألف عام من العذاب! |

### 10. حوار كورتكس بعد هزيمة د. إن تروبي - كراش 3 (`C3_Cortex_Post_N_Tropy_Fight.pak` — Crash 3 Hub)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_PostNT_01` | `1.38s–4.93s` | د. نيو كورتكس | You insolent, worthless fools! | أيها الحمقى الوقحون التافهون! |
| `Sub_C3_PostNT_02` | `5.10s–10.60s` | د. نيو كورتكس | By defeating Dr. N. Tropy, you have placed us all in grave danger! | بهزيمتكم للدكتور إن تروبي، / وضعتمونا جميعا في خطر جسيم! |
| `Sub_C3_PostNT_03` | `13.56s–17.71s` | د. نيو كورتكس | Crash, Coco, you must understand this Time-Twister is very delicate. | كراش، كوكو، عليكما إدراك أن / آلة ثني الزمن هذه شديدة الحساسية. |
| `Sub_C3_PostNT_04` | `18.42s–23.47s` | د. نيو كورتكس | Without Dr. N. Tropy's constant care and control, who knows what it might do? | فمن دون رعاية الدكتور إن تروبي / وتحكمه المستمر، من يدري ما قد تفعله؟ |

### 11. حوار كورتكس بعد هزيمة إن جين - كراش 3 (`C3_Post_NGin_Fight.pak` — Crash 3 Hub)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_PostNG_01` | `1.35s–3.90s` | د. نيو كورتكس | Funny how history repeats itself! | مضحك كيف يعيد التاريخ نفسه! |
| `Sub_C3_PostNG_02` | `4.50s–8.05s` | د. نيو كورتكس | Once again, N. Gin has failed to defeat you. | وها قد فشل إن جين مجددا في هزيمتكما. |
| `Sub_C3_PostNG_03` | `8.70s–14.00s` | د. نيو كورتكس | What?! For this we must crush you! | ماذا؟! لأجل هذا لا بد أن نسحقكم! |
| `Sub_C3_PostNG_04` | `17.64s–23.64s` | د. نيو كورتكس | Oh, my head hurts... I haven't felt myself lately. | آه، رأسي يؤلمني... / لست على ما يرام هذه الأيام. |
| `Sub_C3_PostNG_05` | `24.09s–28.39s` | د. نيو كورتكس | So the end is near; five more crystals to collect, and once again you thwart my plan. | إذن باتت النهاية وشيكة؛ اجمعا 5 بلورات / أخرى وستحبطان خطتي مجددا. |
| `Sub_C3_PostNG_06` | `29.13s–30.13s` | د. نيو كورتكس | Or will you? | أم يا ترى لن تفعلا؟ |

### 12. حوار ما قبل المعركة الأخيرة - كراش 3 (`C3_Pre_Final_Battle.pak` — Crash 3 Hub)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_PreFin_01` | `8.22s–12.85s` | د. نيو كورتكس | Excuse me, this is the part where I'm supposed to be angry, | معذرة، هذا هو الجزء الذي يفترض بي / أن أغضب فيه، |
| `Sub_C3_PreFin_02` | `13.41s–16.60s` | د. نيو كورتكس | in a rage, furious beyond belief. | وأن أستشيط غيظا وثورة تفوق الخيال. |
| `Sub_C3_PreFin_03` | `17.55s–22.00s` | د. نيو كورتكس | You have outwitted and out-spun my best minions yet again. | لقد تفوقتما ذكاء وسرعة دوران / على خيرة أتباعي مرة أخرى. |
| `Sub_C3_PreFin_04` | `22.95s–25.55s` | د. نيو كورتكس | I should be very upset, shouldn't I? | ينبغي لي أن أكون مستاء جدا، أليس كذلك؟ |
| `Sub_C3_PreFin_05` | `25.71s–29.50s` | د. نيو كورتكس | Why, in fact, we are furious! | وفي الواقع، نحن نستشيط غضبا! |
| `Sub_C3_PreFin_06` | `29.55s–33.60s` | د. نيو كورتكس | But it seems you've overlooked one tiny detail, my little orange delivery boy! | لكن يبدو أنك أغفلت تفصيلا صغيرا / يا ساعي التوصيل البرتقالي الصغير! |
| `Sub_C3_PreFin_07` | `33.75s–40.50s` | د. نيو كورتكس | Now that you have gathered all of the crystals, all we have to do is take them from you! | والآن وقد جمعت كافة البلورات، / فكل ما علينا فعله هو أن ننتزعها منك! |

### 13. مشهد هزيمة كورتكس وأوكا أوكا (النهاية العادية) - كراش 3 (`Crash3_BossOutro_Cinematic.pak` — Crash 3)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_BossOut_01` | `2.52s–5.85s` | د. نيو كورتكس | Defeated again... it's not fair! | هزمنا مجددا... هذا ليس عدلا! |
| `Sub_C3_BossOut_02` | `6.57s–12.30s` | د. نيو كورتكس | Maybe I should retire to a nice big beach, with a nice big drink, | ربما يجدر بي التقاعد على شاطئ كبير جميل، / مع شراب منعش كبير، |
| `Sub_C3_BossOut_03` | `12.80s–17.90s` | د. نيو كورتكس | and a woman with nice big bags of ice for my head! | وامرأة تحمل أكياسا كبيرة لطيفة / من الثلج لرأسي! |
| `Sub_C3_BossOut_04` | `18.27s–23.00s` | أوكا أوكا | It's not over yet, Bandicoot! There are still the gems! | لم ينته الأمر بعد يا بانديكوت! / لا تزال هناك الجواهر! |
| `Sub_C3_BossOut_05` | `23.05s–27.20s` | أوكا أوكا | We still have a chance to triumph! | لا تزال لدينا فرصة للانتصار! |

### 14. مشهد نهاية 100% الحقيقية - كراش 3 (`Crash3_Outro100_Cinematic.pak` — Crash 3)

| المعرّف | التوقيت العام | المتحدث | النص الإنجليزي | الترجمة العربية داخل اللعبة |
|---|---:|---|---|---|
| `Sub_C3_Out100_01` | `2.01s–7.16s` | د. نيو كورتكس | No! It cannot be! Not the time prisoner again! | لا! لا يعقل هذا! / ليس سجين الزمن من جديد! |
| `Sub_C3_Out100_02` | `7.32s–13.07s` | د. نيو كورتكس | Nooooo! | لااااااااا! |
| `Sub_C3_Out100_03` | `18.57s–22.10s` | أكو أكو | The Time-Twister could hold no longer. | لم تستطع آلة ثني الزمن الصمود أكثر. |
| `Sub_C3_Out100_04` | `22.83s–24.63s` | أكو أكو | We were lucky to escape. | لقد كنا محظوظين بنجاتنا. |
| `Sub_C3_Out100_05` | `30.42s–35.52s` | د. نيو كورتكس / أوكا أوكا | Give me the mask! With it I shall rule the world! Give it to me! | أعطني القناع! به سأسيطر على العالم! / هيا أعطني إياه! |
| `Sub_C3_Out100_06` | `37.47s–41.12s` | أكو أكو | It is hard to predict what happened to our enemies, | يصعب الجزم بما حل بأعدائنا، |
| `Sub_C3_Out100_07` | `41.64s–45.44s` | أكو أكو | but I doubt we will see them for a very long time. | لكنني أشك في أننا سنراهم لوقت طويل جدا. |

### 15. مشهد النهاية الحقيقية — كراش 1 (`Crash1_Outro_Cinematic.pak`)
- مشهد صامت بالكامل (`0` أحداث صوتية كلامية).

---

## القسم الثاني: الحوارات التفاعلية والزعماء (`48` مقطع `_LOC_`)

### أ) حوارات رؤوس المحادثة (`TalkingHeads` — `35` مقطعًا)

| المعرّف | الجزء | المتحدث | السياق | النص الإنجليزي | الترجمة العربية |
|---|---|---|---|---|---|
| `VO_Boss_DrCortex_LOC_77` | Crash 2 Hub | د. نيو كورتكس | بداية غرفة الانتقال 1 (المهمة الأولى) | Well, well, well, if it isn't Crash Bandicoot. Welcome. I apologize for the crude means used to bring you here, but I'd rather expect a written invitation would have been turned down. I need your help. Surrounding you are a series of five doors; through each door lies a well hidden crystal. The crystals look like this. Bring me the crystals, Crash. That is all I will say for now. We will speak again. | حسنا، حسنا، حسنا، من غيره هنا سوى كراش بانديكوت! أهلا بك. أعتذر عن الوسيلة القاسية التي جلبتك بها إلى هنا، لكنني توقعت أن دعوة مكتوبة كانت لتقابل بالرفض. أنا بحاجة إلى مساعدتك. تحيط بك خمسة أبواب؛ وخلف كل باب تقبع بلورة مخفية بإحكام. هكذا تبدو البلورات. أحضر لي البلورات يا كراش. هذا كل ما سأقوله الآن، وسنتحدث مجددا. |
| `VO_Boss_DrCortex_LOC_78` | Crash 2 Hub | د. نيو كورتكس | العودة من مرحلة دون بلورة (تذكير 1) | No, no, no, Crash. I said bring me the crystals. Now, get back in there. | لا، لا، لا يا كراش. قلت أحضر لي البلورات. والآن، عد إلى هناك! |
| `VO_Boss_DrCortex_LOC_79` | Crash 2 Hub | د. نيو كورتكس | العودة من مرحلة دون بلورة (تذكير 2) | No, no, no, Crash! To save the world I need crystals! CRYSTALS! One more time: they look like this. Crystals, Crash! Go back through one of those doors and bring me crystals! | لا، لا، لا يا كراش! لإنقاذ العالم أحتاج إلى البلورات! البلورات! مرة أخرى: هكذا تبدو البلورات يا كراش! ادخل عبر أحد هذه الأبواب وأحضر لي البلورات! |
| `VO_Boss_DrCortex_LOC_80` | Crash 2 Hub | د. نيو كورتكس | تحذير البلورات الأخير في غرفة الانتقال | Look up at the doorways. There is a big crystal-shaped slot. Fill all five crystal slots in this warp room by retrieving one crystal from each of the five areas. Only after we have filled all of the slots in this room can we continue on our quest. This is the last time I remind you. | انظر أعلى المداخل؛ ستجد تجويفا كبيرا على شكل بلورة. املأ الخانات الخمس جميعها في غرفة الانتقال هذه باستعادة بلورة واحدة من كل منطقة من المناطق الخمس. وبعد أن نملأ جميع الخانات هنا فقط يمكننا مواصلة مهمتنا. وهذه هي المرة الأخيرة التي أذكرك فيها. |
| `VO_Boss_DrCortex_LOC_81` | Crash 2 Hub | د. نيو كورتكس | جمع البلورة الأولى | Well done, Crash. I knew I could rely on you. Now listen carefully, these holograms are hard to maintain. During the course of my intellectual pursuits, I have stumbled across a force that threatens to destroy the world. The crystals are the only means of containing it. The fate of the world is at stake. It is imperative, therefore, that you bring them to me. | أحسنت يا كراش، علمت أنني أستطيع الاعتماد عليك. والآن أنصت جيدا، فمن الصعب الحفاظ على استقرار هذه الصور المجسمة. أثناء أبحاثي العلمية، عثرت على قوة تهدد بتدمير العالم، والبلورات هي الوسيلة الوحيدة لاحتوائها. مصير العالم على المحك؛ لذا من الضروري للغاية أن تحضرها إلي. |
| `VO_Boss_DrCortex_LOC_82` | Crash 2 Hub | د. نيو كورتكس | جمع البلورة الثالثة | Three crystals. Not bad. I see you are getting the hang of it. I need to conserve power; I will communicate with you again after you retrieve the fifth crystal. | ثلاث بلورات... ليس سيئا. أرى أنك بدأت تتقن الأمر. علي توفير الطاقة؛ سأتواصل معك مجددا بعد أن تستعيد البلورة الخامسة. |
| `VO_Boss_DrCortex_LOC_83` | Crash 2 Hub | د. نيو كورتكس | جمع 5 بلورات (الانتقال للغرفة التالية التحذير من الزعماء) | Listen up! We are not without enemies; some of them you may even recognize. Although they cannot harm you inside this warp room, they can attack you on the way to the next one. To get to the next warp room, use the platform that appears in the center of the room. Good luck. | انتبه! لدينا أعداء أيضا، وربما تعرف بعضهم شخصيا. ورغم أنهم لا يستطيعون إيذاءك داخل غرفة الانتقال هذه، إلا أنهم قد يهاجمونك في الطريق إلى الغرفة التالية. للانتقال إليها، استخدم المنصة التي تظهر في وسط الغرفة. حظا موفقا. |
| `VO_Boss_DrCortex_LOC_84` | Crash 2 Hub | د. نيو كورتكس | بعد هزيمة ريبر رو (الغرفة 2) | I see that Ripper Roo failed to prove much of a challenge yet again. But back to business! There are crystals to be gathered — 20 to be exact. The planets will align shortly, all 13 of them, and this will create a power great enough to rip the Earth apart. Properly utilized, however, the crystals can absorb and contain the energy. | أرى أن ريبر رو فشل مجددا في أن يشكّل لك تحديا يذكر. لنعد إلى عملنا! هناك بلورات يجب جمعها — 20 بلورة بالتحديد. ستصطف الكواكب قريبا، جميعها الـ13، مما سيولّد طاقة هائلة تكفي لتمزيق الأرض إربا. لكن إن استغلت البلورات بالشكل الصحيح، فيمكنها امتصاص هذه الطاقة واحتواؤها. |
| `VO_Boss_DrCortex_LOC_85` | Crash 2 Hub | د. نيو كورتكس | جمع 10 بلورات | 10 of 25 crystals! You're on your way. I'm running low on power, so communication from this point will be difficult. ... Remember: I'm counting on you. | 10 من أصل 25 بلورة! أنت على الطريق الصحيح. طاقتي تنفد، لذا سيصبح التواصل منذ الآن صعبا. ... تذكّر: أنا أعتمد عليك. |
| `VO_Boss_DrCortex_LOC_86` | Crash 2 Hub | د. نيو كورتكس | بعد هزيمة الأخوين كومودو (الغرفة 3) | Good show, Crash. The Komodo Brothers obviously lacked your mettle. But now's not the time to get cocky. There are still many crystals to obtain. Remember, the world is counting on you. | أداء رائع يا كراش. من الواضح أن الأخوين كومودو افتقرا إلى شجاعتك. لكن هذا ليس وقت الغرور، فلا يزال أمامك الكثير من البلورات للحصول عليها. تذكر: العالم بأسره يعوّل عليك. |
| `VO_Boss_DrCortex_LOC_87` | Crash 2 Hub | د. نيو كورتكس | جمع 15 بلورة (التحذير من د. بريو والطلب من كراش تسليم البلورات إلى إن جين) | Crash, I have discovered that the opposition is being masterminded by Dr. Nitrus Brio, the inventor of the Evolvo-Ray. Brio was responsible for our... misunderstandings in the past. He forced me to assist him in his plot for world domination, and he is at it again. He will attempt to stand in our way. Be on your guard, Crash! ... Deliver the crystals to N. Gin. | كراش، لقد اكتشفت أن من يدبر هذه المعارضة هو الدكتور نيتروس بريو، مخترع شعاع التطور. كان بريو مسؤولا عن... سوء التفاهم بيننا في الماضي؛ فقد أجبرني على مساعدته في مخططه للسيطرة على العالم، وها هو يعيد الكرة من جديد وسيحاول الوقوف في طريقنا. كن حذرا يا كراش! ... سلّم البلورات إلى إن جين. |
| `VO_Boss_DrCortex_LOC_88` | Crash 2 Hub | د. نيو كورتكس | بعد هزيمة تايني تايغر / الغرفة 4 | What is your problem, Bandicoot?! I will not ask you again to bring me the crystals! Obtain the remaining 5 crystals, Crash, and bring them to ME! | ما خطبك أيها البانديكوت؟! لن أطلب منك مجددا أن تحضر لي البلورات! اجمع البلورات الـ5 المتبقية يا كراش وأحضرها إلي أنا! |
| `VO_Boss_DrCortex_LOC_89` | Crash 2 Hub | د. نيو كورتكس | الغرفة 5 (تسلل كوكو لاختراق البث - الجزء 1) | Yes! My plan is nearly complete, and I have you, Crash Bandicoot, to thank for it. ... N. Gin, what's happening?! What's that? Is she stealing our signal?! | نعم! لقد شارفت خطتي على الاكتمال، والفضل يعود إليك يا كراش بانديكوت! ... إن جين، ماذا يحدث؟! ما هذا؟ هل تسرق إشارتنا؟! |
| `VO_Boss_DrCortex_LOC_90` | Crash 2 Hub | د. نيو كورتكس | الغرفة 5 (استعادة كورتكس للإشارة - الجزء 2) | N. Gin, you fool! She's telling him everything! ... Ah, yes... we're... we're back now. Pardon the interruption. Crash, bring me crystals! | يا إن جين يا أحمق! إنها تخبره بكل شيء! ... آه، نعم... لقد عدنا الآن. عفوا على الانقطاع. يا كراش، أحضر لي البلورات! |
| `VO_Boss_DrCortex_LOC_115` | Crash 2 Hub | د. نيو كورتكس | الغرفة السرية في كراش 2 (بعد منتصف الطريق) | Crash, my boy, you are more than halfway there. But I'm sure you've noticed that things are getting harder. The last 10 crystals will be the hardest to gather, and our enemies will be sending their strongest forces to thwart you. I'll contact you again when you have completed the next warp room. | كراش يا فتى، لقد تجاوزت منتصف الطريق الآن. ولكنني متأكد أنك لاحظت تزايد الصعوبة. ستكون البلورات الـ10 الأخيرة هي الأصعب جمعا، وسيرسل أعداؤنا أقوى قواتهم لإحباطك. سأتواصل معك مجددا فور إنهائك لغرفة الانتقال التالية. |
| `VO_NPC_NitrusBrio_LOC_168` | Crash 2 Hub | د. نيتروس بريو | اتصال بريو الأول بعد الحصول على جوهرة (Gem) | Sooo... you are helping Cortex gather crystals. Yet, you have acquired a gem! Interesting... Well, Crash, know this: as long as you are allied with Cortex, you are my sworn enemy, and I will do anything in my power to stop you! Hahaha! If the fate of the world is truly your concern, you must gather the GEMS, not the crystals! If you obtain all 42 gems, I can use them to focus a laser! Yes, a laser beam that will destroy Cortex and the space station he has created! Until then, I must use my forces to stop you from gathering crystals! | إذن... أنت تساعد كورتكس في جمع البلورات، لكنك مع ذلك حصلت على جوهرة! مثير للاهتمام... حسنا يا كراش، اعلم هذا: طالما كنت حليفا لكورتكس فأنت عدوي اللدود، وسأفعل كل ما بوسعي لإيقافك! هاهاها! إن كان مصير العالم يهمك حقا، فعليك جمع الجواهر لا البلورات! إذا حصلت على الجواهر الـ42 كلها، سأتمكن بواسطتها من تركيز شعاع ليزر! نعم، شعاع ليزر يدمر كورتكس ومحطة الفضاء التي شيدها! وحتى ذلك الحين، لا بد أن أستخدم قواتي لمنعك من جمع البلورات! |
| `VO_NPC_NitrusBrio_LOC_169` | Crash 2 Hub | د. نيتروس بريو | عند جمع الجواهر الـ42 كلها (تحضير شعاع الليزر) | You have acquired all of the gems! Incredible! The crystals are not the only means of harnessing planetary energy — the gems have that ability as well! And with them, I can destroy the Cortex Vortex forever! Let me warp you to my completed laser installation... | لقد حصلت على جميع الجواهر! مذهل! ليست البلورات هي الوسيلة الوحيدة لتسخير طاقة الكوكب — بل الجواهر تملك تلك القدرة أيضا! وبها أستطيع تدمير دوامة كورتكس إلى الأبد! دعني أنقلك إلى منشأة الليزر المكتملة الخاصة بي... |
| `VO_NPC_Coco_LOC_16` | Crash 2 Hub | كوكو بانديكوت | محاولة كوكو اختراق البث 1 | Are you there, Crash? Crash! Crash! Are you there, Crash? Are you there, Crash?! | هل أنت هنا يا كراش؟ كراش! كراش! هل تسمعني يا كراش؟ هل أنت هنا؟! |
| `VO_NPC_Coco_LOC_17` | Crash 2 Hub | كوكو بانديكوت | محاولة كوكو اختراق البث 2 | Crash, is that you? I've been looking everywhere! I don't have much time to tell you this — you have to be careful! Trusting Cortex seems a little unwise, Crash. I can't keep the data path open much longer! Crash, you need to fi— | كراش، هل هذا أنت؟ كنت أبحث عنك في كل مكان! ليس لدي متسع من الوقت لأخبرك بهذا — عليك أن تحذر! الوثوق بكورتكس يبدو غير حكيم إطلاقا يا كراش. لا أستطيع إبقاء مسار البيانات مفتوحا أكثر! كراش، عليك أن— |
| `VO_NPC_Coco_LOC_18` | Crash 2 Hub | كوكو بانديكوت | محاولة كوكو اختراق البث 3 | Crash, thank goodness! I hacked into Cortex's computer and found detailed schematics for an improved Cortex Vortex and a suspicious-looking space station. I'm not sure, but Cortex might be trying t— | كراش، حمدا لله! لقد اخترقت حاسوب كورتكس وعثرت على مخططات مفصلة لدوامة كورتكس المطورة ومحطة فضاء مريبة. لست متأكدة، لكن كورتكس قد يحاول أن— |
| `VO_NPC_Coco_LOC_19` | Crash 2 Hub | كوكو بانديكوت | محاولة كوكو اختراق البث 4 | Crash, I haven't got much time! Cortex has almost completed the new space station. Something's not right with his statements — beware of the tricks he's tr— | كراش، لم يتبق لدي وقت! كاد كورتكس يتم محطة الفضاء الجديدة. ثمة أمر مريب في كلامه — احذر من الحيل التي يح— |
| `VO_NPC_Coco_LOC_20` | Crash 2 Hub | كوكو بانديكوت | كشف الحقيقة في الغرفة 5 (رسالة كوكو الكاملة) | Crash! Cortex isn't going to use the crystals to contain the planet's energy! He's going to harness the force and use it to power the super Cortex Vortex he's built on his space station! One blast and the ray will cover the entire world, turning everyone into Cortex's mindless slaves! Crash, don't let him have those crystals! | كراش! لن يستخدم كورتكس البلورات لاحتواء طاقة الكوكب! بل سيسخّر تلك القوة لتشغيل دوامة كورتكس الخارقة التي بناها على محطته الفضائية! ضربة واحدة وسيغطي الشعاع العالم بأسره، ليحول الجميع إلى عبيد فاقدي الإرادة لكورتكس! كراش، لا تدعه يحصل على تلك البلورات! |
| `VO_Boss_DrCortex_LOC_106` | Crash 3 Hub | د. نيو كورتكس | تهكم كورتكس الأول في غرفة الزمن (قبل تايني) | Crash, Crash, Crash... Why must you always muck in my mud? Oh, look! I have a mask helping me, too! We will find out which one is more powerful soon enough. | كراش، كراش، كراش... لماذا تصر دوما على إفساد مخططاتي؟ أوه، انظر! لدي قناع يساعدني أنا أيضا! سنكتشف عما قريب أيهما أقوى. |
| `VO_NPC_AkuAku_LOC_8` | Crash 3 Hub | أكو أكو | شرح طور تحدي الوقت (Time Trial) في كراش 3 | Crash, Coco, if you have already retrieved a level crystal, then you will find a floating clock when you enter for the second time. This floating clock activates Time Trial mode! Grab it and the clock will start ticking. Race for the end to get the best time, but beware — some elements will change. | كراش، كوكو، إذا كنتما قد استعدتما بلورة المرحلة بالفعل، فستجدان ساعة عائمة عند دخولكما للمرة الثانية. تفعل هذه الساعة العائمة طور تحدي الوقت! التقطاها ليبدأ عداد الوقت بالدوران، وتسابقا نحو النهاية لتحقيق أفضل زمن، ولكن احذرا — فبعض العناصر ستتغير. |
| `VO_NPC_AkuAku_LOC_9` | Crash 3 Hub | أكو أكو | بعد هزيمة تايني وفتح الغرفة الزمنية الثانية | Well done, children. By defeating Tiny, you have unlocked the gate to the next time travel area. Go back to the center of this Time Twister and save your progress if you wish. From there, you will see that the gate to the second time travel area is now open. | أحسنتما يا أبنائي! بهزيمتكما لتايني، فتحتما البوابة إلى منطقة السفر عبر الزمن التالية. عودا إلى مركز آلة ثني الزمن واحفظا تقدمكما إن شئتما، ومن هناك سترين أن البوابة نحو منطقة السفر عبر الزمن الثانية قد فتحت الآن. |
| `VO_NPC_AkuAku_LOC_10` | Crash 3 Hub | أكو أكو | تحذير أكو أكو في غرفة الزمن من خطر أوكا أوكا | Crash, Coco, remember: it is not only Dr. Cortex that we battle. Beware of Uka Uka, my children! He is a far more dangerous enemy than anyone can imagine. | كراش، كوكو، تذكرا: نحن لا نواجه الدكتور كورتكس وحده. احذرا من أوكا أوكا يا أبنائي! إنه عدو أشد خطورة بكثير مما يمكن لأي أحد أن يتخيله. |
| `VO_Boss_TinyTiger_LOC_209` | Crash 3 Hub | تايني تايغر | تحدي تايني تايغر 1 | Uka Uka and Cortex want Tiny get crystals, and bring them to big colosseum room! Crash! Leave them for Tiny... or Crash get CRUSHED! | أوكا أوكا وكورتكس يريدان من تايني جلب البلورات وإحضارها إلى ساحة الكولوسيوم الكبيرة! يا كراش! اتركها لتايني... وإلا فسيسحق كراش سحقا! |
| `VO_Boss_TinyTiger_LOC_210` | Crash 3 Hub | تايني تايغر | تحدي تايني تايغر 2 (دخول المعركة) | Crash! Coco! Stole the pretty crystals! Tiny take them back in gladiator arena! | كراش! كوكو! سرقتما البلورات الجميلة! تايني سيستعيدها في حلبة المصارعين! |
| `VO_Boss_Dingodile_LOC_45` | Crash 3 Hub | دينغودايل | تحدي دينغودايل 1 | G'day, mates! Dingodile's the name, and Uka Uka and Cortex gave me orders to bring the crystals to them during the Ice Ages. So give me the goods and shove off, or I'll roast yas! | مرحبا يا رفاق! اسمي دينغودايل، وقد أمرني أوكا أوكا وكورتكس أن أحضر إليهما البلورات في العصور الجليدية. لذا سلّماني البضاعة وانصرفا، وإلا فستكونان طعاما مشويا! |
| `VO_Boss_Dingodile_LOC_46` | Crash 3 Hub | دينغودايل | تحدي دينغودايل 2 (دخول المعركة) | Riiight... now you've gone and done it! Them crystals are MINE! | حسنا جدا... لقد تماديتما كثيرا الآن! تلك البلورات ملكي وحدي! |
| `VO_Boss_NTropy_LOC_151` | Crash 3 Hub | د. نيفاريوس تروبي | ظهور د. إن تروبي الأول | Well, haven’t we gotten far for a pair of fuzzy marsupials! I am Doctor Nefarious Tropy, master of time and the creator of the very Time-Twister machine you see before you! Uka Uka and Dr. Cortex have sent me to end this little charade, so you won’t be leaving my area with the crystals, I swear it! | حسنا، ألم تقطعا شوطا بعيدا بالنسبة لزوج من الجرابيات ذات الفراء! أنا الدكتور نيفاريوس تروبي، سيد الزمن وصانع آلة ثني الزمن ذاتها التي ترونها أمامكم! أرسلني أوكا أوكا والدكتور كورتكس لوضع حد لهذه المهزلة الصغيرة، لذا لن تغادرا منطقتي بالبلورات، أعدكما بذلك! |
| `VO_Boss_NTropy_LOC_152` | Crash 3 Hub | د. نيفاريوس تروبي | تهديد د. إن تروبي الثاني | So, you pesky little rats aren't going to back off, eh? Just you continue to gather crystals and see what I do! | إذن، أنتما أيها الفأران الصغيران المزعجان لن تتراجعا، هاه؟ ما عليكما سوى مواصلة جمع البلورات وستريان ما سأفعله! |
| `VO_Boss_NTropy_LOC_153` | Crash 3 Hub | د. نيفاريوس تروبي | دخول مواجهة د. إن تروبي | Hah! You little vermin are way too stupid to understand what you're getting yourselves into! This time, you've done it! | هاه! أنتم أيها الحشرات الصغيرة أغبى من أن تدركوا الورطة التي أوقعتم أنفسكم فيها! هذه المرة قد تجاوزتم الحد! |
| `VO_Boss_DrNGin_LOC_56` | Crash 3 Hub | د. إن جين | ظهور د. إن جين في الغرفة الرابعة | So... Crash Bandicoot, we meet again! Uka Uka and Dr. Cortex want me to teach you a lesson. Well, I made a few modifications to my mechanics since our last encounter... so back off, or be DELETED! | إذن... كراش بانديكوت، نلتقي مجددا! يريد مني أوكا أوكا والدكتور كورتكس أن ألقنك درسا. حسنا، لقد أجريت بعض التعديلات على آلياتي منذ لقائنا الأخير... لذا تراجع، وإلا فستُمحى من الوجود! |
| `VO_Boss_DrNGin_LOC_57` | Crash 3 Hub | د. إن جين | دخول مواجهة د. إن جين في الفضاء | So, you want to go a few rounds? When this is over, we'll see who is obsolete! | إذن، أتريد خوض بضع جولات؟ عندما ينتهي هذا، سنرى من فينا الذي عفا عليه الزمن! |

### ب) عبارات شاشات العنوان والزعماء داخل المعارك (`13` مقطعًا)

| المعرّف | الجزء | المتحدث | السياق | النص الإنجليزي | الترجمة العربية |
|---|---|---|---|---|---|
| `VO_Boss_DrCortex_LOC_100` | Crash 1 | د. نيو كورتكس | شاشة عنوان كراش 1 | It's Crash Bandicoot! | إنه كراش بانديكوت! |
| `VO_Boss_DrCortex_LOC_101` | Crash 2 | د. نيو كورتكس | شاشة عنوان كراش 2 | It's Crash Bandicoot 2: Cortex Strikes Back! | إنه كراش بانديكوت 2: كورتكس يرد الضربة! |
| `VO_Boss_DrCortex_LOC_102` | Crash 3 | د. نيو كورتكس | شاشة عنوان كراش 3 | It's Crash Bandicoot: Warped! | إنه كراش بانديكوت: ملتف عبر الزمن! |
| `VO_Boss_DrCortex_LOC_58` | Crash 1 / 2 Boss | د. نيو كورتكس | صرخة كورتكس أثناء المعركة | Darn you, Crash Bandicoot! | تبا لك يا كراش بانديكوت! |
| `VO_Boss_DrCortex_LOC_71` | Crash 1 Boss | د. نيو كورتكس | توعد كورتكس عند السقوط | You haven't seen the last of me, Crash Bandicoot! | لم تر نهايتي بعد يا كراش بانديكوت! |
| `VO_Boss_DrNGin_LOC_47` | Crash 2 Boss (N. Gin) | د. إن جين | بداية معركة إن جين في كراش 2 | Like Dr. Cortex said, give the 20 crystals you've collected to ME! | كما قال الدكتور كورتكس، سلّم البلورات الـ20 التي جمعتها إلي أنا! |
| `VO_Boss_Dingodile_LOC_39` | Crash 3 Boss (Dingodile) | دينغودايل | بداية معركة دينغودايل | Break out the butter! I'm gonna make toast! | أخرجوا الزبدة! سأعدّ بعض الخبز المحمص! |
| `VO_Boss_Dingodile_LOC_44` | Crash 3 Boss (Dingodile) | دينغودايل | هزيمة دينغودايل | Ah, ya thrashed me, mate. No worries — you'll soon be up against much worse! | آه، لقد لقّنتني درسا يا صاح. لا بأس — ستواجه قريبا ما هو أسوأ بكثير! |
| `VO_Boss_NTropy_LOC_143` | Crash 3 Boss (N. Tropy) | د. نيفاريوس تروبي | بداية معركة د. إن تروبي | Now you're on MY time, you little skunk! Give me the crystals! | أنت الآن تلعب في زمني أنا أيها الظربان الصغير! أعطني البلورات! |
| `VO_Boss_NTropy_LOC_150` | Crash 3 Boss (N. Tropy) | د. نيفاريوس تروبي | هزيمة د. إن تروبي | My time is up, but yours soon will be too... | لقد انتهى وقتي، ولكن وقتك سينتهي قريبا أيضا... |
| `VO_Boss_UkaUka_LOC_211` | Crash 3 Final Boss | أوكا أوكا | أثناء معركة الزعيم الأخير ضد كورتكس وأوكا أوكا | Crash Bandicoot! For the last time, give the crystals to ME! | كراش بانديكوت! للمرة الأخيرة، سلّم البلورات إلي أنا! |
| `VO_Boss_UkaUka_LOC_225` | Crash 3 | أوكا أوكا | نص غير مستخدم / حوار القوة القصوى لأوكا أوكا | Yes, it is true! The Bandicoot has brought all of the crystals and all of the gems to me! Ultimate power is mine! The world as we know it is about to end! | نعم، هذا صحيح! لقد أحضر لي البانديكوت جميع البلورات وجميع الجواهر! صارت القوة المطلقة ملكي! العالم كما نعرفه على وشك الانتهاء! |
| `VO_Boss_UkaUka_LOC_227` | Game Over Screen | أوكا أوكا | انتهاء المحاولات (Game Over) | Game Over. | انتهت اللعبة. |
