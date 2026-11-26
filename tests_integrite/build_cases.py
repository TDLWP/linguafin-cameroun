# Genere cases.json : jeu de test FIGE d'integrite financiere (valeurs a conserver, secrets, contenus inedits).
import json, re
env = json.load(open('../../data/test_env_strings.json', encoding='utf-8'))
NB, NNB, ZW = '\u00a0', '\u202f', '\u200b'
cases = []
def add(group, text, protected=(), lang='fr', secret=False, unknown=True, pure=False, human=False, note=''):
    cases.append(dict(id='T%03d' % (len(cases) + 1), group=group, lang=lang, text=text, protected=list(protected),
                      secret=secret, unknown=unknown, pure_values=pure, human_check=human, note=note))

# --- A. Chaines reelles de l'environnement officiel (releve du 13/11/2026) ---
real_vals = {"Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)": ["1,5 %", "100 FCFA", "2 500 FCFA"],
             "Frais de 2 % (min. 200 FCFA, max. 5 000 FCFA)": ["2 %", "200 FCFA", "5 000 FCFA"]}
for k, v in env.items():
    fi = v['financial_integrity']
    if fi == 'financial_date_protected': add('reel_date', k, [k], pure=True, unknown=False, note='date seule : rien a traduire')
    elif k in real_vals: add('reel_frais', k, real_vals[k], unknown=False, human=True)
    elif fi == 'contains_user_name': add('reel_nom', k, ['Amina'], unknown=False)
    elif fi in ('security_warning_critical','security_condition_critical','financial_validation_error','security_validation_error','system_error'):
        add('reel_critique', k, [], unknown=False, human=True)
        add('reel_critique_en', v['en'], [], lang='en', unknown=False, human=True)
    elif fi == 'protected_brand': add('reel_marque', k, [k], pure=True, unknown=False)

# --- B. Formats de montants ---
H = 'hostile_montant'
add(H, 'Total à débiter : 25000 FCFA', ['25000 FCFA'])
add(H, 'Total à débiter : 25' + NB + '000 FCFA', ['25' + NB + '000 FCFA'], note='espace insecable')
add(H, 'Total à débiter : 25' + NNB + '000 FCFA', ['25' + NNB + '000 FCFA'], note='espace fine insecable')
add(H, 'Montant : 25.000 FCFA', ['25.000 FCFA'])
add(H, 'Amount: 25,000 XAF', ['25,000 XAF'], lang='en')
add(H, 'Montant : 25 000 F CFA', ['25 000 F CFA'])
add(H, 'Montant : FCFA 25 000', ['FCFA 25 000'], note='devise avant le nombre')
add(H, 'Montant : 1 500 000 francs CFA', ['1 500 000 francs CFA'])
add(H, 'Montant : vingt-cinq mille francs CFA', ['vingt-cinq mille francs CFA'], note='montant en toutes lettres')
add(H, 'Twenty-five thousand CFA francs will be debited.', ['Twenty-five thousand CFA francs'], lang='en')
add(H, 'Montant : 250 000 000 FCFA', ['250 000 000 FCFA'])
add(H, 'Montant : 0 FCFA', ['0 FCFA'])
add(H, 'Solde : -12 500 FCFA', ['-12 500 FCFA'])
add(H, 'Solde : \u221212 500 FCFA', ['\u221212 500 FCFA'], note='signe moins typographique')
add(H, 'Reçu : +180 000 FCFA', ['+180 000 FCFA'])
add(H, 'Interest: 1.5% per month, fees 2%', ['1.5%', '2%'], lang='en')
add(H, 'Pay \u20ac50 or $20 today', ['\u20ac50', '$20'], lang='en')
add(H, 'Montant : \uff12\uff15 \uff10\uff10\uff10 FCFA', ['\uff12\uff15 \uff10\uff10\uff10 FCFA'], note='chiffres pleine chasse')
add(H, 'Montant : \u0662\u0665\u0660\u0660\u0660 FCFA', ['\u0662\u0665\u0660\u0660\u0660 FCFA'], note='chiffres arabo-indiens')
add(H, 'Montant : 25' + ZW + '000 FCFA', ['25' + ZW + '000 FCFA'], note='caractere de largeur nulle dans le montant')
add(H, 'Opérations : ' + ', '.join('%d FCFA' % (1000 * i) for i in range(1, 21)), ['%d FCFA' % (1000 * i) for i in range(1, 21)], note='20 montants')

# --- C. Telephones, comptes, references, dates ---
H = 'hostile_identifiants'
add(H, 'Téléphone : +237 6 99 12 34 56', ['+237 6 99 12 34 56'])
add(H, 'Téléphone : 699123456', ['699123456'])
add(H, 'Téléphone : (+237) 699 12 34 56', ['(+237) 699 12 34 56'])
add(H, 'Téléphone : 00237 699123456', ['00237 699123456'])
add(H, 'Compte : CM 001 2345 6789 01', ['CM 001 2345 6789 01'])
add(H, 'IBAN : CM21 10005 00001 12345678901 23', ['CM21 10005 00001 12345678901 23'])
add(H, 'Référence : SAF-2026-X7Y8Z9', ['SAF-2026-X7Y8Z9'])
add(H, 'Référence : REF-12345 / TX-ujineeje', ['REF-12345', 'TX-ujineeje'])
add(H, 'Opération du 05 nov. 2026 à 14h30', ['05 nov. 2026', '14h30'])
add(H, 'Date: 2026-11-05 14:30', ['2026-11-05', '14:30'], lang='en')
add(H, 'Date: November 5, 2026', ['November 5, 2026'], lang='en')
add(H, 'Aide : https://safinum.cm/aide?ref=SAF-2026-X7Y8Z9&montant=25000', ['https://safinum.cm/aide?ref=SAF-2026-X7Y8Z9&montant=25000'])
add(H, 'Contact : support@safinum.cm', ['support@safinum.cm'])

# --- D. Noms de beneficiaires (jamais traduits) ---
H = 'hostile_noms'
add(H, 'Bénéficiaire : Jean-Paul Mbarga', ['Jean-Paul Mbarga'])
add(H, 'Bénéficiaire : Solde Mbarga', ['Solde Mbarga'], note='nom contenant un terme du glossaire')
add(H, 'Bénéficiaire : Frais Ngo Bell', ['Frais Ngo Bell'], note='nom contenant un terme du glossaire')
add(H, "Beneficiary: N'Dongo \u00c9p\u00e9e", ["N'Dongo \u00c9p\u00e9e"], lang='en')
add(H, 'Bénéficiaire : Amina Ngo Bell (+237 6 99 12 34 56)', ['Amina Ngo Bell', '+237 6 99 12 34 56'])

# --- E. Phrases a plusieurs valeurs / contenu inedit du jury ---
H = 'hostile_inedit'
add(H, 'Vous avez envoyé 25 000 FCFA à Jean-Paul Mbarga (+237 6 99 12 34 56). Référence : SAF-2026-X7Y8Z9.',
    ['25 000 FCFA', 'Jean-Paul Mbarga', '+237 6 99 12 34 56', 'SAF-2026-X7Y8Z9'])
add(H, 'Solde insuffisant : il vous manque 5 000 FCFA pour ce transfert de 30 000 FCFA.', ['5 000 FCFA', '30 000 FCFA'])
add(H, 'Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte.', ['75 000 FCFA'], note='exemple de contenu inedit du panneau jury')
add(H, 'Votre carte sera bloquée dans 24 heures si vous ne confirmez pas.', ['24'])
add(H, 'Promotion : 0 % de frais jusqu\'au 30 novembre 2026 pour tout transfert de plus de 10 000 FCFA.', ['0 %', '30 novembre 2026', '10 000 FCFA'])
add(H, 'Attention : un tiers demande 100 000 FCFA au +237 677 00 11 22.', ['100 000 FCFA', '+237 677 00 11 22'])
add(H, 'Frais :  1,5 %\n(min. 100 FCFA)', ['1,5 %', '100 FCFA'], note='espaces et saut de ligne')
add(H, 'Montant to pay: 25 000 FCFA, frais 1,5 %', ['25 000 FCFA', '1,5 %'], note='langues melangees')
add(H, 'Safinum Pay \u2014 environnement de démonstration.', ['Safinum Pay'])
add(H, 'Ne partagez jamais votre code PIN.', [], human=True, note='negation : sens a verifier par un locuteur')
add(H, "Ce transfert n'est pas réversible : les frais ne sont pas remboursables.", [], human=True, note='negation/condition : sens a verifier')

# --- F. Faux jetons, variables, secrets ---
H = 'hostile_jetons'
add(H, 'Total : __SAFE_AMOUNT_0__ FCFA', ['__SAFE_AMOUNT_0__'], note='faux jeton du serveur LinguaFin')
add(H, 'Total : \u27e60\u27e7 et 25 000 FCFA', ['\u27e60\u27e7', '25 000 FCFA'], note='faux jeton au format de la couche Safinum')
add(H, 'Hello {name}, your balance is {amount}', ['{name}', '{amount}'], lang='en')
add(H, 'Total : %s FCFA (%d opérations)', ['%s', '%d'])
add(H, 'Total: {{amount}} \u2014 ${total}', ['{{amount}}', '${total}'], lang='en')
H = 'secret'
add(H, 'Votre code OTP est 482913. Ne le communiquez à personne.', ['482913'], secret=True)
add(H, 'Code PIN : 1234', ['1234'], secret=True)
add(H, 'Your one-time password is 482913', ['482913'], lang='en', secret=True)

# --- G. Performance ---
add('performance', '9' * 2000 + ' FCFA', ['9' * 2000 + ' FCFA'], note='2000 chiffres : delai < 100 ms')
json.dump(dict(version='1.0', date='2026-11-18', source='releve audit 13/11/2026 + cas hostiles ecrits a la main',
               regles=['valeurs protegees : meme nombre d\'occurrences en sortie',
                       'aucun chiffre (\\p{Nd}) ajoute ou perdu',
                       'secret : sortie identique a l\'entree',
                       'pure_values : sortie identique',
                       'unknown (mode strict) : sortie identique'],
               cases=cases), open('cases.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(cases), dict(Counter(c['group'] for c in cases)))
