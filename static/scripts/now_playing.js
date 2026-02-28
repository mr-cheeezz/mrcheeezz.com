document.addEventListener("DOMContentLoaded", function () {
  const spotifyWidget = document.getElementById("now-playing-widget");
  if (!spotifyWidget) {
    return;
  }
  const homePage = typeof isHome !== "undefined"
    ? Boolean(isHome)
    : window.location.pathname === "/" || window.location.pathname === "/home";
  const onAdminPath = window.location.pathname.startsWith("/admin");

  const userId = (spotifyWidget.dataset.userId || "").trim();
  const spotifyEndpoint = userId
    ? "/api/spotify/now-playing-card/" + encodeURIComponent(userId)
    : "/api/spotify/now-playing-card";
  const gameEndpoint = "/api/game";

  const cover = document.getElementById("np-cover");
  const link = document.getElementById("np-link");
  const track = document.getElementById("np-track");
  const artist = document.getElementById("np-artist");
  const progress = document.getElementById("np-progress");
  const current = document.getElementById("np-current");
  const total = document.getElementById("np-total");
  const gameWidget = document.querySelector(".game-status");
  const gameName = document.querySelector(".game-name");
  const gameIcon = document.querySelector(".game-icon use");
  const gameIconLink = document.getElementById("game-icon-link");
  const gameNameLink = document.getElementById("game-name-link");
  const gamePlatform = document.querySelector(".game-platform");
  const gameLinksEnabled = gameWidget
    ? String(gameWidget.dataset.linksEnabled || "true").toLowerCase() === "true"
    : true;
  const hiddenClass = "hidden";

  let progressMs = 0;
  let durationMs = 0;
  let spotifyPlaying = false;
  let gameVisible = false;

  function setSpotifyWidgetVisible(visible) {
    spotifyWidget.classList.toggle(hiddenClass, !visible);
  }

  function setGameWidgetVisible(visible) {
    if (!gameWidget) {
      return;
    }
    gameVisible = visible;
    gameWidget.classList.toggle(hiddenClass, !visible);
  }

  function isWidgetVisible(el) {
    if (!el) {
      return false;
    }
    if (el.classList.contains(hiddenClass)) {
      return false;
    }
    const style = window.getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden";
  }

  function applyWidgetLayout() {
    if (!gameWidget) {
      return;
    }

    if (onAdminPath) {
      setSpotifyWidgetVisible(false);
      setGameWidgetVisible(false);
      return;
    }

    const stacked = (
      (spotifyPlaying || isWidgetVisible(spotifyWidget)) &&
      (gameVisible || isWidgetVisible(gameWidget))
    );
    const spotifyRect = spotifyWidget.getBoundingClientRect();
    const viewportWidth = window.innerWidth || document.documentElement.clientWidth;
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight;
    const computedBottom = parseFloat(window.getComputedStyle(spotifyWidget).bottom || "0");
    const spotifyBottom = Number.isFinite(computedBottom)
      ? Math.max(0, computedBottom)
      : Math.max(0, viewportHeight - spotifyRect.bottom);
    const spotifyRightPx = Math.max(0, viewportWidth - spotifyRect.right);
    const spotifyRight = spotifyRightPx + "px";
    const spotifyVisualWidth = Math.max(0, spotifyRect.width);
    const stackGap = 0;
    const stackedBottom = Math.max(0, spotifyBottom + spotifyRect.height + stackGap) + "px";
    if (homePage) {
      gameWidget.classList.toggle("is-stacked", stacked);
      spotifyWidget.classList.toggle("is-stacked", stacked);
      gameWidget.style.setProperty("right", spotifyRight, "important");
      gameWidget.style.setProperty(
        "bottom",
        stacked ? stackedBottom : spotifyBottom + "px",
        "important"
      );
      if (spotifyVisualWidth > 0) {
        gameWidget.style.setProperty("width", spotifyVisualWidth + "px", "important");
      }
      gameWidget.style.setProperty("border-radius", "10px 0 0 0", "important");
      spotifyWidget.style.setProperty(
        "border-radius",
        gameVisible ? "0px" : "10px 0 0 0",
        "important"
      );
      return;
    }

    gameWidget.classList.toggle("is-stacked", stacked);
    spotifyWidget.classList.toggle("is-stacked", stacked);
    gameWidget.style.setProperty("right", spotifyRight, "important");
    gameWidget.style.setProperty(
      "bottom",
      stacked ? stackedBottom : spotifyBottom + "px",
      "important"
    );
    if (spotifyVisualWidth > 0) {
      gameWidget.style.setProperty("width", spotifyVisualWidth + "px", "important");
    }
    gameWidget.style.setProperty(
      "border-radius",
      stacked ? "10px 10px 0 0" : "10px",
      "important"
    );
    spotifyWidget.style.setProperty(
      "border-radius",
      stacked ? "0 0 10px 10px" : "10px",
      "important"
    );
  }

  function formatTime(ms) {
    const seconds = Math.max(0, Math.floor(ms / 1000));
    const mins = Math.floor(seconds / 60);
    const secs = String(seconds % 60).padStart(2, "0");
    return mins + ":" + secs;
  }

  function cleanGameTitle(rawTitle) {
    if (!rawTitle) {
      return "";
    }

    // Remove leading bracketed tags like:
    // [NEW UPDATE] [BETA] Game Name -> Game Name
    let title = String(rawTitle).replace(/^\s*(?:\[[^\]]*\]\s*)+/g, "");
    title = title.replace(/\s+/g, " ").trim();
    return title || String(rawTitle).trim();
  }

  function setLinkState(el, url) {
    if (!el) {
      return;
    }
    const href = String(url || "").trim();
    const enabled = Boolean(href && href !== "#");
    el.href = enabled ? href : "#";
    el.classList.toggle("is-link-disabled", !enabled);
    el.setAttribute("aria-disabled", enabled ? "false" : "true");
  }

  function paintProgress() {
    const pct = durationMs > 0 ? Math.min(100, (progressMs / durationMs) * 100) : 0;
    progress.style.width = pct + "%";
    current.textContent = formatTime(progressMs);
    total.textContent = formatTime(durationMs);
  }

  function paintIdle(message) {
    track.textContent = message || "Nothing is playing";
    artist.textContent = "Spotify is idle";
    link.href = "#";
    cover.removeAttribute("src");
    progressMs = 0;
    durationMs = 0;
    spotifyPlaying = false;
    paintProgress();
    setSpotifyWidgetVisible(false);
    applyWidgetLayout();
  }

  function refreshGameStatus() {
    if (!gameWidget || !gameName || !gameIcon || !gamePlatform) {
      return;
    }

    fetch(gameEndpoint)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("bad response");
        }
        return response.json();
      })
      .then(function (data) {
        const activeGame = cleanGameTitle((data.game || data.steam || data.roblox || "").trim());
        if (!activeGame) {
          setGameWidgetVisible(false);
          applyWidgetLayout();
          return;
        }

        gameName.textContent = activeGame;
        gameName.style.animation = "none";

        if (data.steam) {
          gameWidget.classList.remove("is-roblox");
          gamePlatform.textContent = "Steam";
          gameIcon.setAttribute("href", "/static/images/steam.svg#steam");
          setLinkState(gameIconLink, gameLinksEnabled ? (data.steam_profile_url || data.profile_url) : "");
          setLinkState(gameNameLink, gameLinksEnabled ? (data.steam_game_url || data.game_url) : "");
        } else {
          gameWidget.classList.add("is-roblox");
          gamePlatform.textContent = "Roblox";
          gameIcon.setAttribute("href", "/static/images/roblox.svg#roblox");
          setLinkState(gameIconLink, gameLinksEnabled ? (data.roblox_profile_url || data.profile_url) : "");
          setLinkState(gameNameLink, gameLinksEnabled ? (data.roblox_game_url || data.game_url) : "");
        }
        setGameWidgetVisible(true);
        applyWidgetLayout();
      })
      .catch(function () {
        gameWidget.classList.remove("is-roblox");
        setGameWidgetVisible(false);
        applyWidgetLayout();
      });
  }

  function refreshNowPlaying() {
    fetch(spotifyEndpoint)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("bad response");
        }
        return response.json();
      })
      .then(function (data) {
        if (data.state === "error" && data.connect_url) {
          paintIdle("Link Spotify in admin");
          return;
        }
        if (data.state !== "playing" && data.state !== "paused") {
          paintIdle(data.message || "Nothing is playing");
          return;
        }

        track.textContent = data.track || "Unknown Track";
        artist.textContent = data.artist || "Unknown Artist";
        if (data.cover_url) {
          cover.src = data.cover_url;
        }
        link.href = data.track_url || "#";

        progressMs = Number(data.progress_ms || 0);
        durationMs = Number(data.duration_ms || 0);
        spotifyPlaying = Boolean(data.is_playing);
        paintProgress();
        setSpotifyWidgetVisible(spotifyPlaying);
        applyWidgetLayout();
      })
      .catch(function () {
        paintIdle("Unable to load");
      });
  }

  setInterval(function () {
    if (!spotifyPlaying || durationMs <= 0) {
      return;
    }
    progressMs = Math.min(durationMs, progressMs + 1000);
    paintProgress();
  }, 1000);

  setInterval(refreshNowPlaying, 15000);
  setInterval(refreshGameStatus, 5000);
  setSpotifyWidgetVisible(false);
  setGameWidgetVisible(false);
  if (onAdminPath) {
    return;
  }
  applyWidgetLayout();
  refreshNowPlaying();
  refreshGameStatus();
});
