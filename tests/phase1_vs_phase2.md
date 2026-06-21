# Evaluation Comparison: phase1 vs phase2

## Summary

- Questions compared: **15**
- Average latency (phase1): **0.056s**
- Average latency (phase2): **0.026s**
- `Gita perspective` present in phase1: **0/15 (0.0%)**
- `Gita perspective` present in phase2: **15/15 (100.0%)**
- `Supporting verses` present in phase1: **0/15 (0.0%)**
- `Supporting verses` present in phase2: **15/15 (100.0%)**
- Questions where phase2 answer is longer: **15/15 (100.0%)**
- Questions where citations changed: **11/15 (73.3%)**

## Per-question comparison

### What is karma yoga?

- Latency: phase1 = **0.595s**, phase2 = **0.215s**, diff = **-0.38s**
- Citations phase1: `5.11, 13.25, 6.3, 6.20, 18.19`
- Citations phase2: `5.11, 6.3, 6.20, 2.54, 6.37`
- Citation overlap: `5.11, 6.20, 6.3`
- Answer length (words): phase1 = **50**, phase2 = **143**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 5.11.
It says: The yogis, while giving up attachment, perform actions with their body, senses, mind, and intellect, only for the purpose of self-purification.
Sanskrit source: कायेन मनसा बुद्ध्या केवलैरिन्द्रियैरपि |
योगिनः कर्म कुर्वन्ति सङ्गं त्यक्त्वात्मशुद्धये ||५-११||
Citations: 5.11
```

#### phase2 answer

```text
Answer:
The Gita teaches that one should perform prescribed duty without attachment to the fruits of action.

Gita perspective:
This is karma yoga: action offered in the right spirit, free from egoistic claim and anxiety over success or failure.

Supporting verses:
- 5.11: The yogis, while giving up attachment, perform actions with their body, senses, mind, and intellect, only for the purpose of self-purification.
- 6.3: To the soul who is aspiring for perfection in Yog, work without attachment is said to be the means; to the sage who is already elevated in Yog, tranquility in meditation is said to be the means.
- 6.20: When the mind, restrained from material activities, becomes still by the practice of Yog, then the yogi is able to behold the soul through the purified mind, and he rejoices in the inner joy.

Citations:
5.11, 6.3, 6.20
```

### What does Krishna say about acting without attachment to results?

- Latency: phase1 = **0.014s**, phase2 = **0.016s**, diff = **0.002s**
- Citations phase1: `3.36, 14.21, 5.1, 2.54, 6.37`
- Citations phase2: `5.11, 2.48, 2.53, 5.1, 2.49`
- Citation overlap: `5.1`
- Answer length (words): phase1 = **55**, phase2 = **122**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 3.36.
It says: Arjun asked: Why is a person impelled to commit sinful acts, even unwillingly, as if by force, O descendent of Vrishni (Krishna)?
Sanskrit source: अर्जुन उवाच |
अथ केन प्रयुक्तोऽयं पापं चरति पूरुषः |
अनिच्छन्नपि वार्ष्णेय बलादिव नियोजितः ||३-३६||
Citations: 3.36
```

#### phase2 answer

```text
Answer:
The Gita teaches that one should perform prescribed duty without attachment to the fruits of action.

Gita perspective:
This is karma yoga: action offered in the right spirit, free from egoistic claim and anxiety over success or failure.

Supporting verses:
- 5.11: The yogis, while giving up attachment, perform actions with their body, senses, mind, and intellect, only for the purpose of self-purification.
- 2.48: Be steadfast in the performance of your duty, O Arjun, abandoning attachment to success and failure. Such equanimity is called Yog.
- 2.53: When your intellect ceases to be allured by the fruitive sections of the Vedas and remains steadfast in divine consciousness, you will then attain the state of perfect Yog.

Citations:
5.11, 2.48, 2.53
```

### What is equanimity in the Gita?

- Latency: phase1 = **0.014s**, phase2 = **0.014s**, diff = **0.0s**
- Citations phase1: `18.31, 2.54, 18.22, 3.40, 3.28`
- Citations phase2: `18.31, 18.32, 18.20, 4.39, 6.12 – 6.13`
- Citation overlap: `18.31`
- Answer length (words): phase1 = **58**, phase2 = **128**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 18.31.
It says: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
Sanskrit source: यया धर्ममधर्मं च कार्यं चाकार्यमेव च |
अयथावत्प्रजानाति बुद्धिः सा पार्थ राजसी ||१८-३१||
Citations: 18.31
```

#### phase2 answer

```text
Answer:
The Gita teaches equanimity as steadiness of mind amid success and failure, pleasure and pain.

Gita perspective:
This inner balance is a mark of yoga and spiritual maturity, because the person is no longer ruled by dualities.

Supporting verses:
- 18.31: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
- 18.32: That intellect which is shrouded in darkness, imagining irreligion to be religion, and perceiving untruth to be the truth, is of the nature of ignorance, O Parth.
- 18.20: Understand that knowledge to be in the mode of goodness by which a person sees one undivided imperishable reality within all diverse living beings.

Citations:
18.31, 18.32, 18.20
```

### What is Paramatma?

- Latency: phase1 = **0.022s**, phase2 = **0.013s**, diff = **-0.009s**
- Citations phase1: `7.13, 18.22, 7.1, 18.14, 14.21`
- Citations phase2: `15.17, 7.6, 18.46, 2.18, 18.21`
- Citation overlap: `none`
- Answer length (words): phase1 = **47**, phase2 = **144**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 7.13.
It says: Deluded by the three modes of Maya, people in this world are unable to know Me, the imperishable and eternal.
Sanskrit source: त्रिभिर्गुणमयैर्भावैरेभिः सर्वमिदं जगत् |
मोहितं नाभिजानाति मामेभ्यः परमव्ययम् ||७-१३||
Citations: 7.13
```

#### phase2 answer

```text
Answer:
The Gita teaches that Paramatma is the Supreme Lord present within all beings as the inner witness and guide.

Gita perspective:
From the Gita's perspective, the individual soul is distinct, while Paramatma is the indwelling Supreme who accompanies and knows all.

Supporting verses:
- 15.17: Besides these, is the Supreme Divine Personality, who is the indestructible Supreme Soul. He enters the three worlds as the unchanging Controller and supports all living beings.
- 7.6: Know that all living beings are manifested by these two energies of Mine. I am the source of the entire creation, and into Me it again dissolves.
- 18.46: By performing one’s natural occupation, one worships the Creator from whom all living entities have come into being, and by whom the whole universe is pervaded. By such performance of work, a person easily attains per...

Citations:
15.17, 7.6, 18.46
```

### What is the difference between body and soul?

- Latency: phase1 = **0.021s**, phase2 = **0.011s**, diff = **-0.01s**
- Citations phase1: `2.25, 3.42, 3.43, 2.20, 13.35`
- Citations phase2: `2.25, 2.18, 2.24, 2.17, 3.43`
- Citation overlap: `2.25, 3.43`
- Answer length (words): phase1 = **43**, phase2 = **116**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 2.25.
It says: The soul is spoken of as invisible, inconceivable, and unchangeable. Knowing this, you should not grieve for the body.
Sanskrit source: अव्यक्तोऽयमचिन्त्योऽयमविकार्योऽयमुच्यते |
तस्मादेवं विदित्वैनं नानुशोचितुमर्हसि ||२-२५||
Citations: 2.25
```

#### phase2 answer

```text
Answer:
The Bhagavad Gita teaches that one should act according to dharma without selfish attachment to the results.

Gita perspective:
This is the principle of karma yoga: perform action as duty, remain steady in mind, and give up possessiveness over outcomes.

Supporting verses:
- 2.25: The soul is spoken of as invisible, inconceivable, and unchangeable. Knowing this, you should not grieve for the body.
- 2.18: Only the material body is perishable; the embodied soul within is indestructible, immeasurable, and eternal. Therefore, fight, O descendent of Bharat.
- 2.24: The soul is unbreakable and incombustible; it can neither be dampened nor dried. It is everlasting, in all places, unalterable, immutable, and primordial.

Citations:
2.25, 2.18, 2.24
```

### What is steady wisdom?

- Latency: phase1 = **0.021s**, phase2 = **0.013s**, diff = **-0.008s**
- Citations phase1: `18.42, 4.42, 4.38, 4.39, 7.2`
- Citations phase2: `18.42, 4.42, 4.38, 4.39, 7.2`
- Citation overlap: `18.42, 4.38, 4.39, 4.42, 7.2`
- Answer length (words): phase1 = **50**, phase2 = **136**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 18.42.
It says: Tranquility, restraint, austerity, purity, patience, integrity, knowledge, wisdom, and belief in a hereafter—these are the intrinsic qualities of work for Brahmins.
Sanskrit source: शमो दमस्तपः शौचं क्षान्तिरार्जवमेव च |
ज्ञानं विज्ञानमास्तिक्यं ब्रह्मकर्म स्वभावजम् ||१८-४२||
Citations: 18.42
```

#### phase2 answer

```text
Answer:
The Gita teaches equanimity as steadiness of mind amid success and failure, pleasure and pain.

Gita perspective:
This inner balance is a mark of yoga and spiritual maturity, because the person is no longer ruled by dualities.

Supporting verses:
- 18.42: Tranquility, restraint, austerity, purity, patience, integrity, knowledge, wisdom, and belief in a hereafter—these are the intrinsic qualities of work for Brahmins.
- 4.42: Therefore, with the sword of knowledge, cut asunder the doubts that have arisen in your heart. O scion of Bharat, establish yourself in karm yog. Arise, stand up, and take action!
- 4.38: In this world, there is nothing as purifying as divine knowledge. One who has attained purity of mind through prolonged practice of Yog, receives such knowledge within the heart, in due course of time.

Citations:
18.42, 4.42, 4.38
```

### What does the Gita say about desire and anger?

- Latency: phase1 = **0.017s**, phase2 = **0.013s**, diff = **-0.004s**
- Citations phase1: `3.40, 18.31, 3.34, 16.4, 3.37`
- Citations phase2: `18.31, 3.40, 6.24 – 6.25, 6.10, 6.35`
- Citation overlap: `18.31, 3.40`
- Answer length (words): phase1 = **50**, phase2 = **144**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 3.40.
It says: The senses, mind, and intellect are said to be breeding grounds of desire. Through them, it clouds one’s knowledge and deludes the embodied soul.
Sanskrit source: इन्द्रियाणि मनो बुद्धिरस्याधिष्ठानमुच्यते |
एतैर्विमोहयत्येष ज्ञानमावृत्य देहिनम् ||३-४०||
Citations: 3.40
```

#### phase2 answer

```text
Answer:
The Gita teaches that desire, and the anger that follows from frustrated desire, are major obstacles to wisdom and self-mastery.

Gita perspective:
Unchecked desire binds the mind to worldly craving and leads to confusion, loss of judgment, and spiritual decline.

Supporting verses:
- 18.31: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
- 3.40: The senses, mind, and intellect are said to be breeding grounds of desire. Through them, it clouds one’s knowledge and deludes the embodied soul.
- 6.24 – 6.25: Completely renouncing all desires arising from thoughts of the world, one should restrain the senses from all sides with the mind. Slowly and steadily, with conviction in the intellect, the mind will become fixed in G...

Citations:
18.31, 3.40, 6.24 – 6.25
```

### What are the three gunas?

- Latency: phase1 = **0.014s**, phase2 = **0.012s**, diff = **-0.002s**
- Citations phase1: `14.21, 3.28, 3.42, 3.43, 3.27`
- Citations phase2: `14.5, 18.19, 14.18, 3.28, 3.34`
- Citation overlap: `3.28`
- Answer length (words): phase1 = **60**, phase2 = **136**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 14.21.
It says: Arjun inquired: What are the characteristics of those who have gone beyond the three guṇas, O Lord? How do they act? How do they go beyond the bondage of the guṇas?
Sanskrit source: अर्जुन उवाच |
कैर्लिङ्गैस्त्रीन्गुणानेतानतीतो भवति प्रभो |
किमाचारः कथं चैतांस्त्रीन्गुणानतिवर्तते ||१४-२१||
Citations: 14.21
```

#### phase2 answer

```text
Answer:
The Gita teaches that material life is governed by the three gunas: sattva, rajas, and tamas.

Gita perspective:
Spiritual growth involves understanding their influence and ultimately rising beyond them through disciplined and God-centered living.

Supporting verses:
- 14.5: O mighty-armed Arjun, the material energy consists of three guṇas (modes)—sattva (goodness), rajas (passion), and tamas (ignorance). These modes bind the eternal soul to the perishable body.
- 18.19: Knowledge, action, and the doer are declared to be of three kinds in the Sānkhya philosophy, distinguished according to the three modes of material nature. Listen, and I will explain their distinctions to you.
- 14.18: Those situated in the mode of goodness rise upward; those in the mode of passion stay in the middle; and those in the mode of ignorance go downward.

Citations:
14.5, 18.19, 14.18
```

### What is surrender to Krishna?

- Latency: phase1 = **0.014s**, phase2 = **0.012s**, diff = **-0.002s**
- Citations phase1: `5.1, 2.54, 14.21, 18.62, 6.37`
- Citations phase2: `18.62, 12.1, 2.48, 2.55, 5.1`
- Citation overlap: `18.62, 5.1`
- Answer length (words): phase1 = **71**, phase2 = **121**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 5.1.
It says: Arjun said: O Shree Krishna, You praised karm sanyās (the path of renunciation of actions), and You also advised to do karm yog (work with devotion). Please tell me decisively which of the two is more beneficial?
Sanskrit source: अर्जुन उवाच |
संन्यासं कर्मणां कृष्ण पुनर्योगं च शंससि |
यच्छ्रेय एतयोरेकं तन्मे ब्रूहि सुनिश्चितम् ||५-१||
Citations: 5.1
```

#### phase2 answer

```text
Answer:
The Gita teaches that devotion to Krishna is the highest and most direct path to spiritual fulfillment.

Gita perspective:
Bhakti is not merely emotion; it is loving surrender, remembrance, and dedicated service rooted in true knowledge.

Supporting verses:
- 18.62: Surrender exclusively unto Him with your whole being, O Bharat. By His grace, you will attain perfect peace and the eternal abode.
- 12.1: Arjun inquired: Between those who are steadfastly devoted to Your personal form and those who worship the formless Brahman, whom do You consider to be more perfect in Yog?
- 2.48: Be steadfast in the performance of your duty, O Arjun, abandoning attachment to success and failure. Such equanimity is called Yog.

Citations:
18.62, 12.1, 2.48
```

### What is devotion according to the Gita?

- Latency: phase1 = **0.018s**, phase2 = **0.012s**, diff = **-0.006s**
- Citations phase1: `18.31, 7.21, 6.44, 2.7, 3.40`
- Citations phase2: `18.31, 18.34, 2.48, 7.21, 2.31`
- Citation overlap: `18.31, 7.21`
- Answer length (words): phase1 = **58**, phase2 = **126**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 18.31.
It says: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
Sanskrit source: यया धर्ममधर्मं च कार्यं चाकार्यमेव च |
अयथावत्प्रजानाति बुद्धिः सा पार्थ राजसी ||१८-३१||
Citations: 18.31
```

#### phase2 answer

```text
Answer:
The Gita teaches that devotion to Krishna is the highest and most direct path to spiritual fulfillment.

Gita perspective:
Bhakti is not merely emotion; it is loving surrender, remembrance, and dedicated service rooted in true knowledge.

Supporting verses:
- 18.31: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
- 18.34: The steadfast willpower by which one holds on to duty, pleasures, and wealth, out of attachment and desire for rewards, O Arjun, is determination in the mode of passion.
- 2.48: Be steadfast in the performance of your duty, O Arjun, abandoning attachment to success and failure. Such equanimity is called Yog.

Citations:
18.31, 18.34, 2.48
```

### What does the Gita say about self-control?

- Latency: phase1 = **0.018s**, phase2 = **0.014s**, diff = **-0.004s**
- Citations phase1: `18.31, 2.48, 2.31, 3.40, 4.21`
- Citations phase2: `3.40, 18.33, 18.31, 3.43, 2.48`
- Citation overlap: `18.31, 2.48, 3.40`
- Answer length (words): phase1 = **58**, phase2 = **137**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 18.31.
It says: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.
Sanskrit source: यया धर्ममधर्मं च कार्यं चाकार्यमेव च |
अयथावत्प्रजानाति बुद्धिः सा पार्थ राजसी ||१८-३१||
Citations: 18.31
```

#### phase2 answer

```text
Answer:
The Bhagavad Gita teaches that one should act according to dharma without selfish attachment to the results.

Gita perspective:
This is the principle of karma yoga: perform action as duty, remain steady in mind, and give up possessiveness over outcomes.

Supporting verses:
- 3.40: The senses, mind, and intellect are said to be breeding grounds of desire. Through them, it clouds one’s knowledge and deludes the embodied soul.
- 18.33: The steadfast willpower that is developed through Yog, and which sustains the activities of the mind, the life-airs, and the senses, O Parth, is said to be determination in the mode of goodness.
- 18.31: The intellect is considered in the mode of passion when it is confused between righteousness and unrighteousness, and cannot distinguish between right and wrong conduct, O Parth.

Citations:
3.40, 18.33, 18.31
```

### What is the role of duty in the Gita?

- Latency: phase1 = **0.016s**, phase2 = **0.011s**, diff = **-0.005s**
- Citations phase1: `2.31, 3.22, 2.47, 2.48, 3.35`
- Citations phase2: `2.47, 3.35, 2.48, 3.15, 6.1`
- Citation overlap: `2.47, 2.48, 3.35`
- Answer length (words): phase1 = **54**, phase2 = **147**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 2.31.
It says: Besides, considering your duty as a warrior, you should not waver. Indeed, for a warrior, there is no better engagement than fighting for upholding of righteousness.
Sanskrit source: स्वधर्ममपि चावेक्ष्य न विकम्पितुमर्हसि |
धर्म्याद्धि युद्धाच्छ्रेयोऽन्यत्क्षत्रियस्य न विद्यते ||२-३१||
Citations: 2.31
```

#### phase2 answer

```text
Answer:
The Gita teaches that one should perform prescribed duty without attachment to the fruits of action.

Gita perspective:
This is karma yoga: action offered in the right spirit, free from egoistic claim and anxiety over success or failure.

Supporting verses:
- 2.47: You have a right to perform your prescribed duties, but you are not entitled to the fruits of your actions. Never consider yourself to be the cause of the results of your activities, nor be attached to inaction.
- 3.35: It is far better to perform one’s natural prescribed duty, though tinged with faults, than to perform another’s prescribed duty, though perfectly. In fact, it is preferable to die in the discharge of one’s duty, than ...
- 2.48: Be steadfast in the performance of your duty, O Arjun, abandoning attachment to success and failure. Such equanimity is called Yog.

Citations:
2.47, 3.35, 2.48
```

### What does the Gita teach about renunciation?

- Latency: phase1 = **0.017s**, phase2 = **0.013s**, diff = **-0.004s**
- Citations phase1: `6.23, 18.67, 2.48, 18.4, 6.37`
- Citations phase2: `6.23, 18.67, 2.48, 18.4, 6.37`
- Citation overlap: `18.4, 18.67, 2.48, 6.23, 6.37`
- Answer length (words): phase1 = **51**, phase2 = **137**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 6.23.
It says: That state of severance from union with misery is known as Yog. This Yog should be resolutely practiced with determination free from pessimism.
Sanskrit source: तं विद्याद् दुःखसंयोगवियोगं योगसंज्ञितम् |
स निश्चयेन योक्तव्यो योगोऽनिर्विण्णचेतसा ||६-२३||
Citations: 6.23
```

#### phase2 answer

```text
Answer:
The Bhagavad Gita teaches that one should act according to dharma without selfish attachment to the results.

Gita perspective:
This is the principle of karma yoga: perform action as duty, remain steady in mind, and give up possessiveness over outcomes.

Supporting verses:
- 6.23: That state of severance from union with misery is known as Yog. This Yog should be resolutely practiced with determination free from pessimism.
- 18.67: This instruction should never be explained to those who are not austere or to those who are not devoted. It should also not be spoken to those who are averse to listening (to spiritual topics), and especially not to t...
- 2.48: Be steadfast in the performance of your duty, O Arjun, abandoning attachment to success and failure. Such equanimity is called Yog.

Citations:
6.23, 18.67, 2.48
```

### What does the Gita say about meditation?

- Latency: phase1 = **0.019s**, phase2 = **0.013s**, diff = **-0.006s**
- Citations phase1: `6.10, 6.3, 4.42, 2.54, 12.12`
- Citations phase2: `6.10, 6.3, 4.42, 2.54, 12.12`
- Citation overlap: `12.12, 2.54, 4.42, 6.10, 6.3`
- Answer length (words): phase1 = **57**, phase2 = **150**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 6.10.
It says: Those who seek the state of Yog should reside in seclusion, constantly engaged in meditation with a controlled mind and body, getting rid of desires and possessions for enjoyment.
Sanskrit source: योगी युञ्जीत सततमात्मानं रहसि स्थितः |
एकाकी यतचित्तात्मा निराशीरपरिग्रहः ||६-१०||
Citations: 6.10
```

#### phase2 answer

```text
Answer:
The Bhagavad Gita teaches that one should act according to dharma without selfish attachment to the results.

Gita perspective:
This is the principle of karma yoga: perform action as duty, remain steady in mind, and give up possessiveness over outcomes.

Supporting verses:
- 6.10: Those who seek the state of Yog should reside in seclusion, constantly engaged in meditation with a controlled mind and body, getting rid of desires and possessions for enjoyment.
- 6.3: To the soul who is aspiring for perfection in Yog, work without attachment is said to be the means; to the sage who is already elevated in Yog, tranquility in meditation is said to be the means.
- 4.42: Therefore, with the sword of knowledge, cut asunder the doubts that have arisen in your heart. O scion of Bharat, establish yourself in karm yog. Arise, stand up, and take action!

Citations:
6.10, 6.3, 4.42
```

### What is the highest path according to the Gita?

- Latency: phase1 = **0.018s**, phase2 = **0.013s**, diff = **-0.005s**
- Citations phase1: `18.47, 2.54, 3.28, 10.25, 4.35`
- Citations phase2: `18.47, 2.54, 3.28, 10.25, 4.35`
- Citation overlap: `10.25, 18.47, 2.54, 3.28, 4.35`
- Answer length (words): phase1 = **57**, phase2 = **153**
- Has `Gita perspective`: phase1 = **False**, phase2 = **True**
- Has `Supporting verses`: phase1 = **False**, phase2 = **True**

#### phase1 answer

```text
Answer: Based on the retrieved text, the most relevant passage is 18.47.
It says: It is better to do one’s own dharma, even though imperfectly, than to do another’s dharma, even though perfectly. By doing one’s innate duties, a person does not incur sin.
Sanskrit source: श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात् |
स्वभावनियतं कर्म कुर्वन्नाप्नोति किल्बिषम् ||१८-४७||
Citations: 18.47
```

#### phase2 answer

```text
Answer:
The Bhagavad Gita teaches that one should act according to dharma without selfish attachment to the results.

Gita perspective:
This is the principle of karma yoga: perform action as duty, remain steady in mind, and give up possessiveness over outcomes.

Supporting verses:
- 18.47: It is better to do one’s own dharma, even though imperfectly, than to do another’s dharma, even though perfectly. By doing one’s innate duties, a person does not incur sin.
- 2.54: Arjun said : O Keshav, what is the disposition of one who is situated in divine consciousness? How does an enlightened person talk? How does he sit? How does he walk?
- 3.28: O mighty-armed Arjun, illumined persons distinguish the soul as distinct from guṇas and karmas. They perceive that it is only the guṇas (in the shape of the senses, mind, and others) that move among the guṇas (in the ...

Citations:
18.47, 2.54, 3.28
```
