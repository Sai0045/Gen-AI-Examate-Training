import os
import requests

BASE_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER = os.path.join(BASE_FOLDER, "data", "raw")

NHM = "https://nhm.gov.in/New_Updates_2018/NHM_Components/Immunization/"

# official sources from the project card, some have more than one address to try
SOURCES = {
    "unit2_schedule.pdf": [
        "https://main.mohfw.gov.in/sites/default/files/Unit2NationalImmunizationSchedule.pdf",
        "https://mohfw.gov.in/sites/default/files/Unit2NationalImmunizationSchedule.pdf",
        "https://www.mohfw.gov.in/sites/default/files/Unit2NationalImmunizationSchedule.pdf",
    ],
    "national_immunization_schedule.pdf": [
        "https://www.mohfw.gov.in/sites/default/files/National%20Immunization%20Schedule.pdf",
    ],
    "faq_program_manager.pdf": [
        NHM + "Guidelines_for_immunization/FAQ_on_Immunization_for_Program_Manager-English.pdf",
        NHM + "Guildelines_for_immunization/FAQ_on_Immunization_for_Program_Manager-English.pdf",
    ],
    "handbook_medical_officers_2017.pdf": [
        NHM + "Guidelines_for_immunization/Immunization_Handbook_for_Medical_Officers%202017.pdf",
        NHM + "Guildelines_for_immunization/Immunization_Handbook_for_Medical_Officers%202017.pdf",
    ],
    "handbook_page.html": [
        "https://mohfw.gov.in/basicpage/immunization-handbook-medical-officers2017",
    ],
}


def download(name, urls):
    for url in urls:
        for attempt in range(1, 3):
            try:
                response = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
            except requests.exceptions.Timeout:
                print("Timeout", name, "attempt", attempt)
                continue
            except requests.exceptions.RequestException as e:
                print("Could not download", name, "from", url[:45], "-", str(e)[:80])
                break

            path = os.path.join(RAW_FOLDER, name)
            with open(path, "wb") as f:
                f.write(response.content)
            print("Saved", name, "-", len(response.content), "bytes")
            return True
    return False


def main():
    os.makedirs(RAW_FOLDER, exist_ok=True)
    done = 0
    for name, urls in SOURCES.items():
        if download(name, urls):
            done = done + 1
    print("Downloaded", done, "of", len(SOURCES), "files")


if __name__ == "__main__":
    main()
