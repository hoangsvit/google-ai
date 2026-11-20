# ePlus AI Toolkit — Français

> [!NOTE]
> Ce guide est une référence historique complémentaire, **pas la traduction complète à jour**. Consultez d'abord le [README français actuel](../../README.fr.md), surtout avant toute opération susceptible d'entraîner des frais.

[← Traduction française actuelle](../../README.fr.md) · [Documentation home](../README.md) · [English user guide](../USAGE.md)

[English](../../README.md) · [Tiếng Việt](../../README.vi.md) · [简体中文](../../README.zh-CN.md) · [日本語](../../README.ja.md) · [한국어](../../README.ko.md) · [Español](../../README.es.md) · **Français**

**Aperçu macOS :** la [version Mac](../../docs/MACOS-PREVIEW.md) implémente les étapes 0–5. Les étapes 2–5 peuvent entraîner de vrais frais et exigent une confirmation distincte ; la compatibilité des paiements avec un véritable Mac/MuMu reste non vérifiée.

> **Référence principale :** [README en anglais](../../README.md). Cette traduction reprend les usages et avertissements essentiels ; en cas de divergence, consultez le code actuel et la version anglaise.

**ePlus AI Toolkit** est un outil en ligne de commande principalement destiné à **Windows**. Il utilise **PowerShell, Python, ADB, Frida et un émulateur Android (MuMuPlayer)** pour examiner les offres Google AI Pro proposées via Google One / Google Play. L'interface Textual et le CLI reposent sur le même moteur.

![Interface ePlus AI Toolkit](https://github.com/user-attachments/assets/f16cde7e-022f-43bc-97fe-310012b0a5d3)

> [!CAUTION]
> **Outil non officiel ; des frais réels peuvent être facturés.** Les **étapes 2 à 5** peuvent ouvrir un véritable paiement Google Play et appuyer automatiquement sur **Subscribe (S'abonner)**. L'affichage d'une offre, d'un prix initial nul ou d'un message indiquant qu'un paiement a été demandé **ne prouve pas** l'éligibilité, la gratuité, l'activation ni la prolongation de l'abonnement. Avant toute opération, vérifiez dans Google Play le compte, le montant dû aujourd'hui, le prix de renouvellement et la date de facturation. Arrêter l'outil n'annule pas une transaction déjà envoyée.

> [!NOTE]
> **Une vérification de carte peut bloquer temporairement des fonds même si le paiement Google Play indique 0 USD.** Une **préautorisation en attente d'environ 3 USD** (ou d'un autre montant) peut apparaître. **Les 3 USD sont un exemple, pas des frais fixes de Google ni une facturation d'abonnement confirmée.** Cette retenue peut réduire provisoirement le solde disponible. Selon Google, une autorisation n'est pas un achat et disparaît généralement sous **1 à 14 jours ouvrés**, selon la banque. Si la somme devient un débit définitif ou reste bloquée après 14 jours ouvrés, contactez votre banque et Google Payments. [Documentation officielle de Google Play](https://support.google.com/googleplay/answer/6224192?hl=en).

## Avertissement et responsabilité

Ce projet est **indépendant, sans affiliation, parrainage ni approbation officielle** de Google, Google One, Google Play, NetEase ou MuMuPlayer. Le logiciel est fourni **en l'état**, sans garantie concernant les offres, les résultats d'abonnement ou la compatibilité. Utilisez-le uniquement sur vos appareils et comptes ou avec autorisation, conformément aux lois et conditions des plateformes. Consultez la [décharge complète (anglais)](../../DISCLAIMER.md) et les [précautions de sécurité](../../SECURITY.md).

## 1. Prérequis et installation de MuMuPlayer

- **Windows**, PowerShell **5.1+** et Python **3.10+**.
- **Installer MuMuPlayer séparément**, lancer Android avec root et débogage ADB activés.
- Installer **Google Play Store** et **Google One** dans Android, puis se connecter au compte voulu.
- L'outil peut détecter/télécharger **Android SDK Platform-Tools (ADB)** et préparer **Frida 16.5.9** si nécessaire, mais **ne télécharge et n'installe pas MuMuPlayer**. La compatibilité de Frida dépend de la version d'Android.

**Téléchargement officiel de MuMuPlayer :** [mumuplayer.com/download](https://www.mumuplayer.com/download/) (choisir Windows). Évitez les sites non officiels. Consultez le [Wiki d'installation](https://github.com/hoangsvit/google-ai/wiki/Install).

## 2. Télécharger et démarrer

Dans PowerShell :

```powershell
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
.\run-all.ps1
```

Pour une copie déjà téléchargée :

```powershell
git pull --ff-only
.\run-all.ps1
```

La commande **sans arguments** ouvre l'interface Textual ; elle ne lance aucun achat automatiquement. Le programme peut installer/préparer Textual, ADB ou Frida si nécessaire. Il n'est généralement **pas nécessaire** de lancer `setup_env.py` au préalable. La préparation peut modifier l'émulateur, le proxy ou des paramètres réseau.

Si ADB est dans le PATH, vérifiez la connexion :

```powershell
adb devices
```

L'appareil doit être en état `device`, pas `offline` ni `unauthorized`. Voir le [guide de dépannage](../../docs/DETAILED-GUIDE.md).

### Alternative : utiliser une version publiée si le code récent échoue

Si l'exécution de la dernière version du dépôt provoque des erreurs, vous pouvez essayer une **version déjà publiée** depuis [GitHub Releases](https://github.com/hoangsvit/google-ai/releases). Lisez les notes de version et téléchargez un paquet Windows **s'il est joint**. Si seul le téléchargement automatique **Source code (zip)** de GitHub est disponible, téléchargez le ZIP, décompressez-le, ouvrez PowerShell dans le dossier extrait puis exécutez :

```powershell
.\run-all.ps1
```

**Source code (zip) n'est ni un `.exe` compilé ni un programme d'installation.** Conservez cette version dans un **dossier séparé** pour ne pas écraser votre copie actuelle. Une ancienne version peut ne pas inclure les derniers correctifs ; Windows, Python, MuMuPlayer, ADB/Frida et les précautions de paiement restent nécessaires. Si le problème persiste, consultez le [dépannage](../../docs/DETAILED-GUIDE.md) ou [ouvrez une issue](https://github.com/hoangsvit/google-ai/issues).

## 3. Interface Textual

**Check Device & Offers** exécute **Step 1 — Available offers**, pour consulter les offres **sans déclencher de paiement**. Surveillez **Live Status** et **Show technical details** ; l'absence de nouveaux journaux pendant 30 secondes ne signifie pas forcément que l'outil est bloqué.

Dans **Advanced: Run by step** :

| Mode | Fonctionnement |
| --- | --- |
| **One step only** | Exécute uniquement l'étape 0 à 5 sélectionnée |
| **From selected step** | Lance une séquence guidée depuis l'étape 2 à 5 sélectionnée |
| **All: Steps 2–5** | Lance une séquence guidée à partir de l'étape 2 ; l'étape 5 est facultative |

| Étape | Fonction | Risque |
| --- | --- | --- |
| **0 — Environment** | Diagnostic/préparation d'Android, ADB et Frida | Aucun paiement ; peut modifier les paramètres |
| **1 — Available offers** | Consultation des offres Google Play | Aucun paiement ; la préparation peut modifier l'environnement |
| **2 — Pro 12 months** | Ancien processus d'offre de 12 mois | **Paiement réel possible** |
| **3 — Pro +6 months** | Mise à jour de l'abonnement d'origine | **Paiement réel possible** |
| **4 — Pro +6 months (second)** | Seconde mise à jour de l'abonnement | **Paiement réel possible** |
| **5 — Optional +6 months** | Mise à jour facultative | **Paiement réel possible** |

Les durées sont les **anciens noms des étapes** et ne garantissent aucune prolongation. Si vous avez déjà un abonnement actif, **ne relancez pas l'étape 2**.

Dans le TUI, **chaque étape de paiement exige une approbation distincte**. Même si un envoi de paiement est signalé, vérifiez le forfait actif, les frais et le renouvellement dans les [abonnements Google Play](https://play.google.com/store/account/subscriptions). Ne sélectionnez **Verified in Google Play → Next** que si vous avez confirmé personnellement la modification. L'outil **ne prouve pas à lui seul** l'activation.

**Arrêt/sortie :** Stop pour les étapes 0–1 demande l'arrêt du processus local. Pour les étapes 2–5, **Stop after this step** bloque les étapes suivantes, mais **n'interrompt pas de force un paiement en cours**. Pendant un paiement, **Q / Exit** attend la fin de l'étape actuelle. **D** affiche/masque le journal technique ; **R** lance le mode choisi.

## 4. PowerShell CLI (avancé)

**Consultation/diagnostic, sans paiement :**

```powershell
.\run-all.ps1 -Step 1
.\run-all.ps1 -Step 1 -Debug
.\run-all.ps1 -Step 0
.\run-all.ps1 -Cli
```

**Les commandes suivantes peuvent provoquer de vrais paiements :**

```powershell
.\run-all.ps1 -Step 2
.\run-all.ps1 -Step 3
.\run-all.ps1 -Step 4
.\run-all.ps1 -Step 5
```

Contrairement à l'interface Textual, l'exécution isolée de `-Step 2..5` **n'affiche pas de deuxième demande de validation dans PowerShell**. Exécutez ces commandes uniquement si vous souhaitez réellement tenter un paiement et avez vérifié les conditions.

Séquence guidée via CLI :

```powershell
.\run-all.ps1 -AllStages
.\run-all.ps1 -AllStages -StartStep 3
```

Choix CLI : **1 = Continue (continuer), 2 = End run (terminer), 0 = Stop (arrêter)**. Vérifiez Google Play après chaque étape. `-StartStep 3` ne prouve pas la réussite des étapes antérieures.

Paramètres facultatifs :

```powershell
.\run-all.ps1 -Step 1 -Serial emulator-5554
.\run-all.ps1 -AllStages -Email "account@gmail.com"
```

Utilisez uniquement un identifiant de périphérique réellement affiché par ADB. Évitez `-Force` : il désactive la vérification de correspondance du compte, mais **ne contourne pas** les conditions d'éligibilité ni les protections de paiement de Google.

## 5. Dépannage et résultats

- **MuMu/ADB introuvable :** vérifiez l'émulateur, root, l'autorisation ADB et l'état du périphérique.
- **Erreur Frida :** vérifiez les journaux, la version **16.5.9** et la compatibilité Android.
- **Aucune offre :** ouvrez Google One/Play Store et relancez **Step 1**.
- **Mauvais compte :** vérifiez le profil Google Play sans contourner le contrôle.
- **Paiement demandé :** ne signifie pas que l'abonnement a été activé ou prolongé ; vérifiez Google Play avant de réessayer.
- **Erreur de sécurité du paiement (ex. OR-REH-04) :** arrêtez les étapes de paiement et suivez les procédures officielles.

Les journaux se trouvent dans `logs/` et les rapports dans `ultra0-report/`. **Ne partagez pas de données non masquées contenant comptes, jetons ou informations de paiement.** La CI effectue seulement des tests statiques/simulés, **pas de véritables achats**. La prise en charge complète de **macOS** n'est pas disponible.

## Assistance communautaire et projets associés

Si vous rencontrez des problèmes pour installer ou utiliser ePlus AI Toolkit, vous pouvez contacter la communauté et échanger des conseils sur la [publication d'assistance et de discussion Telegram d'ePlus](https://t.me/eplus_news/29). Pour les bugs reproductibles, vous pouvez aussi [ouvrir une issue GitHub](https://github.com/hoangsvit/google-ai/issues). **Ne publiez jamais de mots de passe, de codes OTP/2FA, de jetons d'offre ou d'achat, de journaux non anonymisés ou de données bancaires.** Il ne s'agit pas du support officiel de Google.

**Vous n'êtes pas éligible à l'offre Google AI Pro ?** Vous pouvez découvrir un autre projet communautaire d'ePlus.DEV : [Muse Invite Hub](https://github.com/ePlus-DEV/muse-invite-hub), pour [rechercher ou partager des codes d'invitation Muse](https://muse.eplus.dev/). **Muse est un service distinct** : ses invitations **ne donnent pas accès à Google AI Pro et ne remplacent pas** un abonnement Google AI Pro. La disponibilité des codes et les conditions géographiques ou de compte peuvent varier.

## Documentation et crédits

[README anglais](../../README.md) · [Wiki Install](https://github.com/hoangsvit/google-ai/wiki/Install) · [Guide détaillé](../../docs/DETAILED-GUIDE.md) · [Étapes d'origine](../../docs/ORIGINAL-STEPS.md) · [Décharge](../../DISCLAIMER.md) · [Sécurité](../../SECURITY.md) · [Contribuer](../../CONTRIBUTING.md) · [Mentions légales](../../THIRD_PARTY_NOTICES.md)

**Auteur d'origine :** [@gylive](https://github.com/gylive) — [google-ultra](https://github.com/gylive/google-ultra). **Maintenance :** [David Nguyen (@hoangsvit)](https://github.com/hoangsvit) / [ePlus.DEV](https://eplus.dev). Les mentions MIT de l'auteur initial sont conservées dans `THIRD_PARTY_NOTICES.md`.
