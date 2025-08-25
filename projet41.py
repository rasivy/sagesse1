from playwright.async_api import async_playwright
import asyncio, json, random, itertools


# Charger la liste des comptes
with open("accounts.json", "r", encoding="utf-8") as f:
    ACCOUNTS = json.load(f)

# Charger la liste des pages
with open("pages.json", "r", encoding="utf-8") as f:
    PAGES = json.load(f)
#URLS = [p["url"] for p in PAGES] # Extraire directement les URL

# Charger la liste des commentaires
with open("comments.json", "r", encoding="utf-8") as f:
    COMMENTS = json.load(f)


JSON_FILE_COMMENTED_POSTS = "commented_posts.json"

# Charger la blacklist si elle existe déjà
try:
    with open("blacklist.json", "r", encoding="utf-8") as f:
        BLACKLIST = set(json.load(f))
except:
    BLACKLIST = set()

# Pages en erreur (à retenter)
ERREURS = {}

# Fonction pour charger les posts déjà commentés
def load_commented_posts():
    try:
        with open(JSON_FILE_COMMENTED_POSTS, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

# Fonction pour sauvegarder les posts commentés
def save_commented_posts(posts_set):
    with open(JSON_FILE_COMMENTED_POSTS, "w", encoding="utf-8") as f:
        json.dump(list(posts_set), f, ensure_ascii=False, indent=2)

# Charger les cookies
async def load_cookies(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)
    cookies = []
    for c in raw_cookies:
        cookies.append({
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "expires": c.get("expirationDate", -1)
        })
    return cookies


#async def auto_reload(page, interval_minutes=7):
#    while True:
#        print(f"auto_reload: attente de {interval_minutes} minutes")
#        await asyncio.sleep(interval_minutes * 60)  # attend intervalle
#        try:
#            await page.reload(wait_until="domcontentloaded", timeout=60000)
#            print("🔄 Page rechargée automatiquement")
#        except Exception as e:
#            print(f"Erreur lors du reload automatique: {e}")


# Fonction pour attendre avec timeout
#async def wait_for_post_with_timeout(first_post, timeout_sec=15):
#    try:
#        await asyncio.wait_for(first_post.wait_for(), timeout=timeout_sec)
#        return True
#    except asyncio.TimeoutError:
#        print("⚠️ Timeout atteint, on recharge la page...")
#        return False
    

async def visiter_page(browser, account, url, commented_posts):
    """Essaie de visiter une page avec un compte donné, commenter un post si possible"""
    context = await browser.new_context()

    # Timeout global pour toutes les actions (clic, saisie, wait_for, etc.)
    context.set_default_timeout(180000)  # 7 minutes . click(), fill(), wait_for_selector(), locator.wait_for()
    context.set_default_navigation_timeout(180000) # Timeout global spécifique à la navigation (goto, reload, wait_for_url)

    try:
        cookies = await load_cookies(account)
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(url)
        #await page.goto(url, wait_until="domcontentloaded", timeout=0)
        #await page.locator("article").first.wait_for(timeout=15000)

        # Lancer la tâche de reload automatique en arrière-plan
        #asyncio.create_task(auto_reload(page, interval_minutes=7))

        # --- Scroll et récupération du post avec watchdog ---
        #try:
        #    scroll_times = random.randint(1, 2)
        #    for i in range(scroll_times):
        #        await page.mouse.wheel(0, 2000)
        #        await page.wait_for_timeout(1500)
        #    print(f"scroll {scroll_times} fois")

            # --- Revenir au post le plus récent (nth(0)) ---
        #    first_post = page.locator('[role="article"]').nth(0)
        #    await first_post.scroll_into_view_if_needed()

        #    print("Retour au post le plus récent")
        #    await asyncio.sleep(random.uniform(0.3, 0.5) * 60)
        #    print("stabilise terminé")

            # Utiliser la nouvelle fonction pour attendre le post
        #    found = await wait_for_post_with_timeout(first_post, timeout_sec=15)
        #    if not found:
        #        print("⚠️ Page bloquée, on recharge...")
        #        await page.reload(wait_until="domcontentloaded", timeout=60000)
        #        first_post = page.locator('[role="article"]').nth(0)
        #        await first_post.scroll_into_view_if_needed()
                # Vérifier à nouveau
        #        found = await wait_for_post_with_timeout(first_post, timeout_sec=15)
        #        if not found:
        #            print("❌ Impossible de charger le post après reload.")
        #            await page.close()
        #            await context.close()
        #            return False

            # Récupération du lien du post
        #    post_link_elem = first_post.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0)
        #    post_link = await post_link_elem.get_attribute("href")
        #    good_url = post_link.split("?")[0]
        #    print("Lien du post le plus récent :", good_url)

        #except Exception as e:
        #    print("Blocage détecté, impossible d'obtenir le post")
        #    print(f"page : {url}")
        #    print(f"{e}")
        #    try:
        #        await page.reload(wait_until="domcontentloaded", timeout=60000)
        #        print(f"✅ Page rechargée avec succès {url}")
        #    except Exception as e2:
        #        print("❌ Impossible de recharger :", e2)
        #    await page.close()
        #    await context.close()
        #    return False



        # Scroll pour charger plus de posts
        #await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

        # scroller un petit coup pour forcer le lazy loading du premier post
        #await page.mouse.wheel(0, 1000)

        # Sélectionner le premier post
        #first_post = page.locator('[role="article"]').first
        #first_post = page.locator('[role="article"]').nth(0)


        #
        # Choisir un nombre de scroll aléatoire entre 1 et 3
        #scroll_times = random.randint(2, 5)
        #print(f"👉 Je vais scroller {scroll_times} fois")

        #for i in range(scroll_times):
        #    await page.mouse.wheel(0, 2000)   # Descend de 2000 pixels
        #    await page.wait_for_timeout(1500) # Attente pour laisser charger

        # --- Revenir au post le plus récent (nth(0)) ---
        #first_post = page.locator('[role="article"]').nth(0)
        #await first_post.scroll_into_view_if_needed()
        #print("⬆️ Retour au post le plus récent")
        #await asyncio.sleep(random.uniform(0.3, 0.5) * 60)
        #print("stabilise terminé")
        

        # pas de post trouvé (on recharge la page car c'est peut-etre bloqué à cause de la connexion internet)
        #try:
        #    await first_post.wait_for(timeout=10000)  # 1 min max
        #    print("✅ Post trouvé")

        #    #post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/']").first.get_attribute("href")
        #    post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")
        #    good_url = post_link.split('?')[0]
        #    print("2Lien du post le plus récent :", good_url)

        #except Exception:
        #    print("⚠️ Aucun post trouvé, tentative de reload...")
        #    try:
        #        await page.reload(wait_until="domcontentloaded", timeout=60000)
        #        print(f"✅ Page rechargée avec succès {url}")
        #    except Exception as e:
        #        print("⚠️ Erreur lors du reload :", e)
        #        try:
        #            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        #            print("✅ Navigation réussie après échec du reload")
        #        except Exception as e2:
        #            print("❌ Impossible de recharger ou revisiter :", e2)


        await page.mouse.wheel(0, 600)   # Descend de 2000 pixels
        await page.wait_for_timeout(1500) # Attente pour laisser charger
        first_post = page.locator('[role="article"]').nth(0)
        await first_post.wait_for(timeout=30000)  # 10 minutes max d’attente


        # Choisir un nombre de scroll aléatoire entre 1 et 3
        #scroll_times = random.randint(1, 2)
        #print(f"scroll {scroll_times} fois")

        #for i in range(scroll_times):
        #    await page.mouse.wheel(0, 100)   # Descend de 2000 pixels
        #    await page.wait_for_timeout(1500) # Attente pour laisser charger
        #    await first_post.scroll_into_view_if_needed()

        #await asyncio.sleep(random.uniform(0.3, 0.5) * 60)
        #print("stabilise terminé")

        # Récupérer le lien du post
        #post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/']").nth(0).get_attribute("href")
        post_link = await first_post.locator("a[href*='/posts/'], a[href*='/videos/']").first.get_attribute("href")
        good_url = post_link.split('?')[0]
        #print("Lien du post le plus récent :", good_url)

        # Si pas de post trouvé
        if not post_link:
            print(f"❌ Aucun post trouvé, page inaccessible {url}")
            await page.close()
            await context.close()
            return False

        # Vérifier si le post a déjà été commenté
        if good_url in commented_posts:
            print(f"🔄 Post déjà commenté : {good_url}")
            await page.close()
            await context.close()
            return True  # On considère comme "réussi" puisque déjà commenté
        
        

                # Cliquer sur la zone de commentaire
                #comment_box = page.locator("div[role='textbox']").first
                #await comment_box.click()

        # Cliquer pour ouvrir la zone de commentaire
        comment_box = page.locator("div[role='textbox']").first
        #comment_box = page.locator("div[role='textbox']").nth(0)
        
        #comment_box = first_post.locator("div[role='textbox']").first
        await comment_box.click()
        await asyncio.sleep(1)  # Attente pour que la zone soit active

        comment = random.choice(COMMENTS)
        await comment_box.fill(comment)
        await asyncio.sleep(random.uniform(0.1, 0.3) * 60)
        await page.keyboard.press("Enter")
        print("Commentaire réussi")
        print(f"page : {url}")
        print(f"post : {good_url}")
        print(f"compte : {account} ")
        print("Commentaire :")
        print(f"{comment}")

        # Ajouter le post à la liste des posts commentés
        commented_posts.add(good_url)
        save_commented_posts(commented_posts)

        await asyncio.sleep(random.uniform(0.3, 1) * 60)

        await page.close()
        await context.close()
        return True

    except Exception as e:
        print("Erreur sur une page")
        print(f"{e}")
        print(f"page : {url}")
        print(f"compte : {account} ")
        await context.close()
        return False

async def main():
    commented_posts = load_commented_posts()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        pages_cycle = itertools.cycle(PAGES)
        compteur = 0  # pages parcourues

        while True:  # boucle infinie
            for account in ACCOUNTS:
                #url = next(pages_cycle)
                page_obj = next(pages_cycle)
                url = page_obj["url"]  # 🔹 on récupère une fois

                # ignorer blacklist
                if url in BLACKLIST:
                    print(f"🚫 {url} est dans la blacklist → ignoré")
                    continue

                ok = await visiter_page(browser, account, url, commented_posts)

                if not ok:
                    # Initialiser la liste des comptes qui ont échoué
                    if url not in ERREURS:
                        ERREURS[url] = {"comptes_tentes": []}
                    ERREURS[url]["comptes_tentes"].append(account)

                    # Si tous les comptes ont échoué → blacklist
                    if len(ERREURS[url]["comptes_tentes"]) == len(ACCOUNTS):
                        print(f"⚠️ {url} a échoué avec tous les comptes → blacklisté")
                        BLACKLIST.add(url)
                        with open("blacklist.json", "w", encoding="utf-8") as f:
                            json.dump(list(BLACKLIST), f, indent=2)
                        del ERREURS[url]

            # Retenter les pages en erreur toutes les 3 cycles
            if compteur % 3 == 0 and ERREURS:
                print("🔄 Retente les pages échouées...")
                for failed_url, infos in list(ERREURS.items()):
                    for acc in ACCOUNTS:
                        if acc not in infos["comptes_tentes"]:
                            ok = await visiter_page(browser, acc, failed_url, commented_posts)
                            if ok:
                                print(f"✅ Succès en réessayant {failed_url} avec {acc}")
                                del ERREURS[failed_url]
                                break
                            else:
                                infos["comptes_tentes"].append(acc)
                                if len(infos["comptes_tentes"]) == len(ACCOUNTS):
                                    print(f"⚠️ {failed_url} encore raté avec tous les comptes → blacklist")
                                    BLACKLIST.add(failed_url)
                                    with open("blacklist.json", "w", encoding="utf-8") as f:
                                        json.dump(list(BLACKLIST), f, indent=2)
                                    del ERREURS[failed_url]

                compteur += 1
                #print("⏳ Fin de cycle → pause 1 min")
                #await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())