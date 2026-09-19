import json
import urllib.request
import xbmc
import xbmcgui

JSON_URL = "https://raw.githubusercontent.com/nervix-ui/JumpTo/refs/heads/main/intros.json"

class JumpToPlayer(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.intros_data = []
        self.load_database()

    def load_database(self):
        """Charge la base de données JSON depuis le repo Git."""
        try:
            req = urllib.request.Request(JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                self.intros_data = json.loads(response.read().decode('utf-8'))
            xbmc.log("[JumpTo] Base de données chargée avec succès avec %d éléments" % len(self.intros_data), xbmc.LOGINFO)
        except Exception as e:
            xbmc.log(f"[JumpTo] Erreur lors du chargement du JSON : {e}", xbmc.LOGERROR)

    def onAVStarted(self):
        """Déclenché au lancement d'une vidéo."""
        if not self.isPlayingVideo():
            return

        # Récupération des métadonnées de la vidéo en cours
        show_title = self.getVideoInfoTag().getTVShowTitle()
        season = self.getVideoInfoTag().getSeason()
        episode = self.getVideoInfoTag().getEpisode()
        xbmc.log(f"[JumpTo] Lecture détectée : {show_title} S{season}E{episode}", xbmc.LOGINFO)
        if not show_title or season == -1 or episode == -1:
            return  # Ce n'est pas un épisode de série valide

        # Recherche dans le JSON chargé
        intro_duration = self.find_intro_duration(show_title, season, episode)

        if intro_duration:
            self.prompt_jump(intro_duration)

    def find_intro_duration(self, show, season, episode):
        """Cherche si l'épisode est présent dans le JSON."""
        for item in self.intros_data:
            if (item.get("show").lower() == show.lower() and 
                item.get("season") == season and 
                item.get("episode") == episode):
                return item.get("intro_length")
        return None

    def prompt_jump(self, duration):
        """Affiche la notification/dialogue avec un délai d'expiration de 10 secondes."""
        dialog = xbmcgui.Dialog()
        # Affiche un dialogue de confirmation pendant 10 secondes
        do_jump = dialog.yesno(
            "JumpTo",
            f"Passer le générique d'intro ({duration}s) ?",
            yeslabel="Sauter",
            nolabel="Ignorer",
            autoclose=10000  # Se ferme automatiquement au bout de 10 000 ms (10s)
        )

        if do_jump:
            current_time = self.getTime()
            self.seekTime(current_time + duration)


if __name__ == '__main__':
    player = JumpToPlayer()
    monitor = xbmc.Monitor()

    # Maintient le service actif tant que Kodi est ouvert
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break