from pathlib import Path

path = Path("App.jsx")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        '''const CATEGORY_STORAGE_KEY =
  "github-store-default-category";''',
        '''const CATEGORY_STORAGE_KEY =
  "github-store-default-category";

const DOWNLOAD_LOCATION_STORAGE_KEY =
  "github-store-download-location";''',
    ),
    (
        '''  const [downloadingAll, setDownloadingAll] =
    useState(false);''',
        '''  const [downloadingAll, setDownloadingAll] =
    useState(false);

  const [downloadLocation, setDownloadLocation] =
    useState(() => {
      try {
        return localStorage.getItem(
          DOWNLOAD_LOCATION_STORAGE_KEY
        ) || "";
      } catch {
        return "";
      }
    });

  const [downloadLocationError, setDownloadLocationError] =
    useState("");''',
    ),
    (
        '''  const isEditorDirty = useMemo(
''',
        '''  const persistDownloadLocation = async (location) => {
    const value = String(location || "").trim();

    try {
      if (value) {
        localStorage.setItem(
          DOWNLOAD_LOCATION_STORAGE_KEY,
          value
        );
      } else {
        localStorage.removeItem(
          DOWNLOAD_LOCATION_STORAGE_KEY
        );
      }
    } catch (error) {
      console.error(
        "Failed to save download location:",
        error
      );
    }

    setDownloadLocation(value);

    const setter =
      window.electronAPI?.downloads?.setDirectory ||
      window.electronAPI?.setDownloadDirectory;

    if (setter) {
      try {
        await setter(value || null);
      } catch (error) {
        console.error(
          "Failed to apply download location:",
          error
        );
      }
    }
  };

  const handleChooseDownloadLocation = async () => {
    setDownloadLocationError("");

    const picker =
      window.electronAPI?.downloads?.chooseDirectory ||
      window.electronAPI?.chooseDownloadDirectory ||
      window.electronAPI?.selectDownloadFolder;

    if (picker) {
      try {
        const result = await picker();
        const selectedPath =
          typeof result === "string"
            ? result
            : result?.path || result?.directory || result?.folderPath;

        if (selectedPath) {
          await persistDownloadLocation(selectedPath);
        }

        return;
      } catch (error) {
        console.error(
          "Failed to choose download location:",
          error
        );

        setDownloadLocationError(
          error?.message ||
            "Could not choose a download folder."
        );
        return;
      }
    }

    if (typeof window.showDirectoryPicker === "function") {
      try {
        const handle = await window.showDirectoryPicker();
        if (handle?.name) {
          await persistDownloadLocation(handle.name);
        }
        return;
      } catch (error) {
        if (error?.name === "AbortError") return;

        console.error(
          "Failed to choose download location:",
          error
        );

        setDownloadLocationError(
          error?.message ||
            "Could not choose a download folder."
        );
        return;
      }
    }

    setDownloadLocationError(
      "Folder selection is not available in this build yet."
    );
  };

  const handleClearDownloadLocation = async () => {
    await persistDownloadLocation("");
    setDownloadLocationError("");
  };

''',
    ),
    (
        '''          selectedRelease.id,
          asset.id
        );''',
        '''          selectedRelease.id,
          asset.id,
          downloadLocation || undefined
        );''',
    ),
    (
        '''            {/* CATEGORY SETTINGS */}''',
        '''            {/* DOWNLOAD SETTINGS */}
            <div className="settings-card">
              <div>
                <h3>Download location</h3>
                <p>
                  Choose where GitHub Store should save downloaded app files.
                </p>
                <div
                  style={{
                    marginTop: "10px",
                    color: "#777",
                    fontSize: "13px",
                    wordBreak: "break-all",
                  }}
                >
                  {downloadLocation || "Default Downloads folder"}
                </div>

                {downloadLocationError && (
                  <div
                    className="auth-error"
                    style={{ marginTop: "12px" }}
                  >
                    {downloadLocationError}
                  </div>
                )}
              </div>

              <div
                style={{
                  display: "flex",
                  gap: "10px",
                  alignItems: "center",
                  flexWrap: "wrap",
                }}
              >
                <button
                  className="secondary-button"
                  type="button"
                  onClick={handleChooseDownloadLocation}
                >
                  Change location
                </button>

                {downloadLocation && (
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={handleClearDownloadLocation}
                  >
                    Use default
                  </button>
                )}
              </div>
            </div>

            {/* CATEGORY SETTINGS */}''',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Patch target not found:\n{old[:160]}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("Download location patch applied successfully.")
