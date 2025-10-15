import requests as req
import json
import sys
import os
from datetime import datetime
from typing import Dict

# Function to print colored text
def print_colored(text: str, color: str) -> None:
    """
    Print colored text.

    Args:
        text: Text to be printed.
        color: Color to be applied to the text.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_text: str = f"{color_code}{text}\033[0m"
    print(colored_text)

# Function to get user input with colored prompt
def input_colored(prompt: str, color: str) -> str:
    """
    Get user input with colored prompt.

    Args:
        prompt: Prompt to be displayed to the user.
        color: Color of the prompt.

    Returns:
        User input.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_prompt: str = f"{color_code}{prompt}\033[0m"
    return input(colored_prompt)

# Hardcoded voices data (no external JSON file needed)
# Hardcoded voices data (no external JSON file needed)
# Extracted from speechma.com - 583 voices across 76 languages
def load_voices():
    return {
    "Multilingual": {
        "United States": {
            "male": {
                "Andrew Multilingual": "voice-1",
                "Brian Multilingual": "voice-3"
            },
            "female": {
                "Ava Multilingual": "voice-2",
                "Emma Multilingual": "voice-4"
            }
        },
        "France": {
            "male": {
                "Remy Multilingual": "voice-5"
            },
            "female": {
                "Vivienne Multilingual": "voice-6"
            }
        },
        "Germany": {
            "male": {
                "Florian Multilingual": "voice-7"
            },
            "female": {
                "Seraphina Multilingual": "voice-8"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Multilingual": "voice-9"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Multilingual": "voice-10"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Multilingual": "voice-11"
            }
        }
    },
    "English": {
        "United States": {
            "female": {
                "Ana": "voice-12",
                "Aria": "voice-14",
                "Ava": "voice-15",
                "Emma": "voice-18",
                "Jenny": "voice-21",
                "Michelle": "voice-22"
            },
            "male": {
                "Andrew": "voice-13",
                "Brian": "voice-16",
                "Christopher": "voice-17",
                "Eric": "voice-19",
                "Guy": "voice-20",
                "Roger": "voice-23",
                "Steffan": "voice-24"
            }
        },
        "United Kingdom": {
            "female": {
                "Libby": "voice-25",
                "Maisie": "voice-26",
                "Sonia": "voice-28"
            },
            "male": {
                "Ryan": "voice-27",
                "Thomas": "voice-29"
            }
        },
        "Australia": {
            "female": {
                "Natasha": "voice-30"
            },
            "male": {
                "William": "voice-31"
            }
        },
        "Canada": {
            "female": {
                "Clara": "voice-32"
            },
            "male": {
                "Liam": "voice-33"
            }
        },
        "India": {
            "female": {
                "Neerja Expressive": "voice-34",
                "Neerja": "voice-35"
            },
            "male": {
                "Prabhat": "voice-36"
            }
        },
        "Hong Kong": {
            "male": {
                "Sam": "voice-37"
            },
            "female": {
                "Yan": "voice-38"
            }
        },
        "Ireland": {
            "male": {
                "Connor": "voice-39"
            },
            "female": {
                "Emily": "voice-40"
            }
        },
        "Kenya": {
            "female": {
                "Asilia": "voice-41"
            },
            "male": {
                "Chilemba": "voice-42"
            }
        },
        "Nigeria": {
            "male": {
                "Abeo": "voice-43"
            },
            "female": {
                "Ezinne": "voice-44"
            }
        },
        "New Zealand": {
            "male": {
                "Mitchell": "voice-45"
            },
            "female": {
                "Molly": "voice-46"
            }
        },
        "Philippines": {
            "male": {
                "James": "voice-47"
            },
            "female": {
                "Rosa": "voice-48"
            }
        },
        "Singapore": {
            "female": {
                "Luna": "voice-49"
            },
            "male": {
                "Wayne": "voice-50"
            }
        },
        "Tanzania": {
            "male": {
                "Elimu": "voice-51"
            },
            "female": {
                "Imani": "voice-52"
            }
        },
        "South Africa": {
            "female": {
                "Leah": "voice-53"
            },
            "male": {
                "Luke": "voice-54"
            }
        }
    },
    "Spanish": {
        "Argentina": {
            "female": {
                "Elena": "voice-55"
            },
            "male": {
                "Tomas": "voice-56"
            }
        },
        "Bolivia": {
            "male": {
                "Marcelo": "voice-57"
            },
            "female": {
                "Sofia": "voice-58"
            }
        },
        "Chile": {
            "female": {
                "Catalina": "voice-59"
            },
            "male": {
                "Lorenzo": "voice-60"
            }
        },
        "Colombia": {
            "male": {
                "Gonzalo": "voice-61"
            },
            "female": {
                "Salome": "voice-62"
            }
        },
        "Costa Rica": {
            "male": {
                "Juan": "voice-63"
            },
            "female": {
                "Maria": "voice-64"
            }
        },
        "Cuba": {
            "female": {
                "Belkys": "voice-65"
            },
            "male": {
                "Manuel": "voice-66"
            }
        },
        "Dominican Republic": {
            "male": {
                "Emilio": "voice-67"
            },
            "female": {
                "Ramona": "voice-68"
            }
        },
        "Ecuador": {
            "female": {
                "Andrea": "voice-69"
            },
            "male": {
                "Luis": "voice-70"
            }
        },
        "Spain": {
            "male": {
                "Alvaro": "voice-71"
            },
            "female": {
                "Elvira": "voice-72",
                "Ximena": "voice-73"
            }
        },
        "Equatorial Guinea": {
            "male": {
                "Javier": "voice-74"
            },
            "female": {
                "Teresa": "voice-75"
            }
        },
        "Guatemala": {
            "male": {
                "Andres": "voice-76"
            },
            "female": {
                "Marta": "voice-77"
            }
        },
        "Honduras": {
            "male": {
                "Carlos": "voice-78"
            },
            "female": {
                "Karla": "voice-79"
            }
        },
        "Mexico": {
            "female": {
                "Dalia": "voice-80"
            },
            "male": {
                "Jorge": "voice-81"
            }
        },
        "Nicaragua": {
            "male": {
                "Federico": "voice-82"
            },
            "female": {
                "Yolanda": "voice-83"
            }
        },
        "Panama": {
            "female": {
                "Margarita": "voice-84"
            },
            "male": {
                "Roberto": "voice-85"
            }
        },
        "Peru": {
            "male": {
                "Alex": "voice-86"
            },
            "female": {
                "Camila": "voice-87"
            }
        },
        "Puerto Rico": {
            "female": {
                "Karina": "voice-88"
            },
            "male": {
                "Victor": "voice-89"
            }
        },
        "Paraguay": {
            "male": {
                "Mario": "voice-90"
            },
            "female": {
                "Tania": "voice-91"
            }
        },
        "El Salvador": {
            "female": {
                "Lorena": "voice-92"
            },
            "male": {
                "Rodrigo": "voice-93"
            }
        },
        "United States": {
            "male": {
                "Alonso": "voice-94",
                "Andrew Spanish": "voice-320",
                "Brian Spanish": "voice-322"
            },
            "female": {
                "Paloma": "voice-95",
                "Ava Spanish": "voice-321",
                "Emma Spanish": "voice-323"
            }
        },
        "Uruguay": {
            "male": {
                "Mateo": "voice-96"
            },
            "female": {
                "Valentina": "voice-97"
            }
        },
        "Venezuela": {
            "female": {
                "Paola": "voice-98"
            },
            "male": {
                "Sebastian": "voice-99"
            }
        },
        "France": {
            "male": {
                "Remy Spanish": "voice-324"
            },
            "female": {
                "Vivienne Spanish": "voice-325"
            }
        },
        "Germany": {
            "male": {
                "Florian Spanish": "voice-326"
            },
            "female": {
                "Seraphina Spanish": "voice-327"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Spanish": "voice-328"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Spanish": "voice-329"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Spanish": "voice-330"
            }
        }
    },
    "Chinese": {
        "China": {
            "female": {
                "Xiaoxiao": "voice-100",
                "Xiaoyi": "voice-101",
                "Xiaobei": "voice-106",
                "Xiaoni": "voice-107"
            },
            "male": {
                "Yunjian": "voice-102",
                "Yunxi": "voice-103",
                "Yunxia": "voice-104",
                "Yunyang": "voice-105"
            }
        },
        "Hong Kong": {
            "female": {
                "HiuGaai": "voice-108",
                "HiuMaan": "voice-109"
            },
            "male": {
                "WanLung": "voice-110"
            }
        },
        "Taiwan": {
            "female": {
                "HsiaoChen": "voice-111",
                "HsiaoYu": "voice-112"
            },
            "male": {
                "YunJhe": "voice-113"
            }
        },
        "United States": {
            "male": {
                "Andrew Chinese": "voice-386",
                "Brian Chinese": "voice-388"
            },
            "female": {
                "Ava Chinese": "voice-387",
                "Emma Chinese": "voice-389"
            }
        },
        "France": {
            "male": {
                "Remy Chinese": "voice-390"
            },
            "female": {
                "Vivienne Chinese": "voice-391"
            }
        },
        "Germany": {
            "male": {
                "Florian Chinese": "voice-392"
            },
            "female": {
                "Seraphina Chinese": "voice-393"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Chinese": "voice-394"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Chinese": "voice-395"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Chinese": "voice-396"
            }
        }
    },
    "French": {
        "Belgium": {
            "female": {
                "Charline": "voice-114"
            },
            "male": {
                "Gerard": "voice-115"
            }
        },
        "Canada": {
            "male": {
                "Antoine": "voice-116",
                "Jean": "voice-117",
                "Thierry": "voice-119"
            },
            "female": {
                "Sylvie": "voice-118"
            }
        },
        "Switzerland": {
            "female": {
                "Ariane": "voice-120"
            },
            "male": {
                "Fabrice": "voice-121"
            }
        },
        "France": {
            "female": {
                "Denise": "voice-122",
                "Eloise": "voice-123",
                "Vivienne French": "voice-336"
            },
            "male": {
                "Henri": "voice-124",
                "Remy French": "voice-335"
            }
        },
        "United States": {
            "male": {
                "Andrew French": "voice-331",
                "Brian French": "voice-333"
            },
            "female": {
                "Ava French": "voice-332",
                "Emma French": "voice-334"
            }
        },
        "Germany": {
            "male": {
                "Florian French": "voice-337"
            },
            "female": {
                "Seraphina French": "voice-338"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe French": "voice-339"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu French": "voice-340"
            }
        },
        "Brazil": {
            "female": {
                "Thalita French": "voice-341"
            }
        }
    },
    "German": {
        "Austria": {
            "female": {
                "Ingrid": "voice-125"
            },
            "male": {
                "Jonas": "voice-126"
            }
        },
        "Switzerland": {
            "male": {
                "Jan": "voice-127"
            },
            "female": {
                "Leni": "voice-128"
            }
        },
        "Germany": {
            "female": {
                "Amala": "voice-129",
                "Katja": "voice-131",
                "Seraphina German": "voice-349"
            },
            "male": {
                "Conrad": "voice-130",
                "Killian": "voice-132",
                "Florian German": "voice-348"
            }
        },
        "United States": {
            "male": {
                "Andrew German": "voice-342",
                "Brian German": "voice-344"
            },
            "female": {
                "Ava German": "voice-343",
                "Emma German": "voice-345"
            }
        },
        "France": {
            "male": {
                "Remy German": "voice-346"
            },
            "female": {
                "Vivienne German": "voice-347"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe German": "voice-350"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu German": "voice-351"
            }
        },
        "Brazil": {
            "female": {
                "Thalita German": "voice-352"
            }
        }
    },
    "Arabic": {
        "United Arab Emirates": {
            "female": {
                "Fatima": "voice-133"
            },
            "male": {
                "Hamdan": "voice-134"
            }
        },
        "Bahrain": {
            "male": {
                "Ali": "voice-135"
            },
            "female": {
                "Laila": "voice-136"
            }
        },
        "Algeria": {
            "female": {
                "Amina": "voice-137"
            },
            "male": {
                "Ismael": "voice-138"
            }
        },
        "Egypt": {
            "female": {
                "Salma": "voice-139"
            },
            "male": {
                "Shakir": "voice-140"
            }
        },
        "Iraq": {
            "male": {
                "Bassel": "voice-141"
            },
            "female": {
                "Rana": "voice-142"
            }
        },
        "Jordan": {
            "female": {
                "Sana": "voice-143"
            },
            "male": {
                "Taim": "voice-144"
            }
        },
        "Kuwait": {
            "male": {
                "Fahed": "voice-145"
            },
            "female": {
                "Noura": "voice-146"
            }
        },
        "Lebanon": {
            "female": {
                "Layla": "voice-147"
            },
            "male": {
                "Rami": "voice-148"
            }
        },
        "Libya": {
            "female": {
                "Iman": "voice-149"
            },
            "male": {
                "Omar": "voice-150"
            }
        },
        "Morocco": {
            "male": {
                "Jamal": "voice-151"
            },
            "female": {
                "Mouna": "voice-152"
            }
        },
        "Oman": {
            "male": {
                "Abdullah": "voice-153"
            },
            "female": {
                "Aysha": "voice-154"
            }
        },
        "Qatar": {
            "female": {
                "Amal": "voice-155"
            },
            "male": {
                "Moaz": "voice-156"
            }
        },
        "Saudi Arabia": {
            "male": {
                "Hamed": "voice-157"
            },
            "female": {
                "Zariyah": "voice-158"
            }
        },
        "Syria": {
            "female": {
                "Amany": "voice-159"
            },
            "male": {
                "Laith": "voice-160"
            }
        },
        "Tunisia": {
            "male": {
                "Hedi": "voice-161"
            },
            "female": {
                "Reem": "voice-162"
            }
        },
        "Yemen": {
            "female": {
                "Maryam": "voice-163"
            },
            "male": {
                "Saleh": "voice-164"
            }
        },
        "United States": {
            "male": {
                "Andrew Arabic": "voice-408",
                "Brian Arabic": "voice-410"
            },
            "female": {
                "Ava Arabic": "voice-409",
                "Emma Arabic": "voice-411"
            }
        },
        "France": {
            "male": {
                "Remy Arabic": "voice-412"
            },
            "female": {
                "Vivienne Arabic": "voice-413"
            }
        },
        "Germany": {
            "male": {
                "Florian Arabic": "voice-414"
            },
            "female": {
                "Seraphina Arabic": "voice-415"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Arabic": "voice-416"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Arabic": "voice-417"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Arabic": "voice-418"
            }
        }
    },
    "Afrikaans": {
        "South Africa": {
            "female": {
                "Adri": "voice-165"
            },
            "male": {
                "Willem": "voice-166"
            }
        }
    },
    "Albanian": {
        "Albania": {
            "female": {
                "Anila": "voice-167"
            },
            "male": {
                "Ilir": "voice-168"
            }
        }
    },
    "Amharic": {
        "Ethiopia": {
            "male": {
                "Ameha": "voice-169"
            },
            "female": {
                "Mekdes": "voice-170"
            }
        }
    },
    "Azerbaijani": {
        "Azerbaijan": {
            "male": {
                "Babek": "voice-171"
            },
            "female": {
                "Banu": "voice-172"
            }
        }
    },
    "Bengali": {
        "Bangladesh": {
            "female": {
                "Nabanita": "voice-173"
            },
            "male": {
                "Pradeep": "voice-174"
            }
        },
        "India": {
            "male": {
                "Bashkar": "voice-175"
            },
            "female": {
                "Tanishaa": "voice-176"
            }
        }
    },
    "Bosnian": {
        "Bosnia and Herzegovina": {
            "male": {
                "Goran": "voice-177"
            },
            "female": {
                "Vesna": "voice-178"
            }
        }
    },
    "Bulgarian": {
        "Bulgaria": {
            "male": {
                "Borislav": "voice-179"
            },
            "female": {
                "Kalina": "voice-180"
            }
        }
    },
    "Burmese": {
        "Myanmar": {
            "female": {
                "Nilar": "voice-181"
            },
            "male": {
                "Thiha": "voice-182"
            }
        }
    },
    "Catalan": {
        "Spain": {
            "male": {
                "Enric": "voice-183"
            },
            "female": {
                "Joana": "voice-184"
            }
        }
    },
    "Croatian": {
        "Croatia": {
            "female": {
                "Gabrijela": "voice-185"
            },
            "male": {
                "Srecko": "voice-186"
            }
        }
    },
    "Czech": {
        "Czech Republic": {
            "male": {
                "Antonin": "voice-187"
            },
            "female": {
                "Vlasta": "voice-188"
            }
        }
    },
    "Danish": {
        "Denmark": {
            "female": {
                "Christel": "voice-189"
            },
            "male": {
                "Jeppe": "voice-190"
            }
        },
        "United States": {
            "male": {
                "Andrew Danish": "voice-474",
                "Brian Danish": "voice-476"
            },
            "female": {
                "Ava Danish": "voice-475",
                "Emma Danish": "voice-477"
            }
        },
        "France": {
            "male": {
                "Remy Danish": "voice-478"
            },
            "female": {
                "Vivienne Danish": "voice-479"
            }
        },
        "Germany": {
            "male": {
                "Florian Danish": "voice-480"
            },
            "female": {
                "Seraphina Danish": "voice-481"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Danish": "voice-482"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Danish": "voice-483"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Danish": "voice-484"
            }
        }
    },
    "Dutch": {
        "Belgium": {
            "male": {
                "Arnaud": "voice-191"
            },
            "female": {
                "Dena": "voice-192"
            }
        },
        "Netherlands": {
            "female": {
                "Colette": "voice-193",
                "Fenna": "voice-194"
            },
            "male": {
                "Maarten": "voice-195"
            }
        },
        "United States": {
            "male": {
                "Andrew Dutch": "voice-441",
                "Brian Dutch": "voice-443"
            },
            "female": {
                "Ava Dutch": "voice-442",
                "Emma Dutch": "voice-444"
            }
        },
        "France": {
            "male": {
                "Remy Dutch": "voice-445"
            },
            "female": {
                "Vivienne Dutch": "voice-446"
            }
        },
        "Germany": {
            "male": {
                "Florian Dutch": "voice-447"
            },
            "female": {
                "Seraphina Dutch": "voice-448"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Dutch": "voice-449"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Dutch": "voice-450"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Dutch": "voice-451"
            }
        }
    },
    "Estonian": {
        "Estonia": {
            "female": {
                "Anu": "voice-196"
            },
            "male": {
                "Kert": "voice-197"
            }
        }
    },
    "Filipino": {
        "Philippines": {
            "male": {
                "Angelo": "voice-198"
            },
            "female": {
                "Blessica": "voice-199"
            }
        },
        "United States": {
            "male": {
                "Andrew Filipino": "voice-562",
                "Brian Filipino": "voice-564"
            },
            "female": {
                "Ava Filipino": "voice-563",
                "Emma Filipino": "voice-565"
            }
        },
        "France": {
            "male": {
                "Remy Filipino": "voice-566"
            },
            "female": {
                "Vivienne Filipino": "voice-567"
            }
        },
        "Germany": {
            "male": {
                "Florian Filipino": "voice-568"
            },
            "female": {
                "Seraphina Filipino": "voice-569"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Filipino": "voice-570"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Filipino": "voice-571"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Filipino": "voice-572"
            }
        }
    },
    "Finnish": {
        "Finland": {
            "male": {
                "Harri": "voice-200"
            },
            "female": {
                "Noora": "voice-201"
            }
        }
    },
    "Galician": {
        "Spain": {
            "male": {
                "Roi": "voice-202"
            },
            "female": {
                "Sabela": "voice-203"
            }
        }
    },
    "Georgian": {
        "Georgia": {
            "female": {
                "Eka": "voice-204"
            },
            "male": {
                "Giorgi": "voice-205"
            }
        }
    },
    "Greek": {
        "Greece": {
            "female": {
                "Athina": "voice-206"
            },
            "male": {
                "Nestoras": "voice-208"
            }
        },
        "United States": {
            "male": {
                "Andrew Greek": "voice-529",
                "Brian Greek": "voice-531"
            },
            "female": {
                "Ava Greek": "voice-530",
                "Emma Greek": "voice-532"
            }
        },
        "France": {
            "male": {
                "Remy Greek": "voice-533"
            },
            "female": {
                "Vivienne Greek": "voice-534"
            }
        },
        "Germany": {
            "male": {
                "Florian Greek": "voice-535"
            },
            "female": {
                "Seraphina Greek": "voice-536"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Greek": "voice-537"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Greek": "voice-538"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Greek": "voice-539"
            }
        }
    },
    "Gujarati": {
        "India": {
            "female": {
                "Dhwani": "voice-209"
            },
            "male": {
                "Niranjan": "voice-210"
            }
        }
    },
    "Hebrew": {
        "Israel": {
            "male": {
                "Avri": "voice-211"
            },
            "female": {
                "Hila": "voice-212"
            }
        }
    },
    "Hindi": {
        "India": {
            "male": {
                "Madhur": "voice-213"
            },
            "female": {
                "Swara": "voice-214"
            }
        },
        "United States": {
            "male": {
                "Andrew Hindi": "voice-419",
                "Brian Hindi": "voice-421"
            },
            "female": {
                "Ava Hindi": "voice-420",
                "Emma Hindi": "voice-422"
            }
        },
        "France": {
            "male": {
                "Remy Hindi": "voice-423"
            },
            "female": {
                "Vivienne Hindi": "voice-424"
            }
        },
        "Germany": {
            "male": {
                "Florian Hindi": "voice-425"
            },
            "female": {
                "Seraphina Hindi": "voice-426"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Hindi": "voice-427"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Hindi": "voice-428"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Hindi": "voice-429"
            }
        }
    },
    "Hungarian": {
        "Hungary": {
            "female": {
                "Noemi": "voice-215"
            },
            "male": {
                "Tamas": "voice-216"
            }
        },
        "United States": {
            "male": {
                "Andrew Hungarian": "voice-518",
                "Brian Hungarian": "voice-520"
            },
            "female": {
                "Ava Hungarian": "voice-519",
                "Emma Hungarian": "voice-521"
            }
        },
        "France": {
            "male": {
                "Remy Hungarian": "voice-522"
            },
            "female": {
                "Vivienne Hungarian": "voice-523"
            }
        },
        "Germany": {
            "male": {
                "Florian Hungarian": "voice-524"
            },
            "female": {
                "Seraphina Hungarian": "voice-525"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Hungarian": "voice-526"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Hungarian": "voice-527"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Hungarian": "voice-528"
            }
        }
    },
    "Icelandic": {
        "Iceland": {
            "female": {
                "Gudrun": "voice-217"
            },
            "male": {
                "Gunnar": "voice-218"
            }
        }
    },
    "Indonesian": {
        "Indonesia": {
            "male": {
                "Ardi": "voice-219"
            },
            "female": {
                "Gadis": "voice-220"
            }
        },
        "United States": {
            "male": {
                "Andrew Indonesian": "voice-540",
                "Brian Indonesian": "voice-542"
            },
            "female": {
                "Ava Indonesian": "voice-541",
                "Emma Indonesian": "voice-543"
            }
        },
        "France": {
            "male": {
                "Remy Indonesian": "voice-544"
            },
            "female": {
                "Vivienne Indonesian": "voice-545"
            }
        },
        "Germany": {
            "male": {
                "Florian Indonesian": "voice-546"
            },
            "female": {
                "Seraphina Indonesian": "voice-547"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Indonesian": "voice-548"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Indonesian": "voice-549"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Indonesian": "voice-550"
            }
        }
    },
    "Irish": {
        "Ireland": {
            "male": {
                "Colm": "voice-221"
            },
            "female": {
                "Orla": "voice-222"
            }
        }
    },
    "Italian": {
        "Italy": {
            "male": {
                "Diego": "voice-223",
                "Giuseppe Italian": "voice-361"
            },
            "female": {
                "Elsa": "voice-224",
                "Isabella": "voice-225"
            }
        },
        "United States": {
            "male": {
                "Andrew Italian": "voice-353",
                "Brian Italian": "voice-355"
            },
            "female": {
                "Ava Italian": "voice-354",
                "Emma Italian": "voice-356"
            }
        },
        "France": {
            "male": {
                "Remy Italian": "voice-357"
            },
            "female": {
                "Vivienne Italian": "voice-358"
            }
        },
        "Germany": {
            "male": {
                "Florian Italian": "voice-359"
            },
            "female": {
                "Seraphina Italian": "voice-360"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Italian": "voice-362"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Italian": "voice-363"
            }
        }
    },
    "Japanese": {
        "Japan": {
            "male": {
                "Keita": "voice-226"
            },
            "female": {
                "Nanami": "voice-227"
            }
        },
        "United States": {
            "male": {
                "Andrew Japanese": "voice-397",
                "Brian Japanese": "voice-399"
            },
            "female": {
                "Ava Japanese": "voice-398",
                "Emma Japanese": "voice-400"
            }
        },
        "France": {
            "male": {
                "Remy Japanese": "voice-401"
            },
            "female": {
                "Vivienne Japanese": "voice-402"
            }
        },
        "Germany": {
            "male": {
                "Florian Japanese": "voice-403"
            },
            "female": {
                "Seraphina Japanese": "voice-404"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Japanese": "voice-405"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Japanese": "voice-406"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Japanese": "voice-407"
            }
        }
    },
    "Javanese": {
        "Indonesia": {
            "male": {
                "Dimas": "voice-228"
            },
            "female": {
                "Siti": "voice-229"
            }
        }
    },
    "Kannada": {
        "India": {
            "male": {
                "Gagan": "voice-230"
            },
            "female": {
                "Sapna": "voice-231"
            }
        }
    },
    "Kazakh": {
        "Kazakhstan": {
            "female": {
                "Aigul": "voice-232"
            },
            "male": {
                "Daulet": "voice-233"
            }
        }
    },
    "Khmer": {
        "Cambodia": {
            "male": {
                "Piseth": "voice-234"
            },
            "female": {
                "Sreymom": "voice-235"
            }
        }
    },
    "Korean": {
        "South Korea": {
            "male": {
                "InJoon": "voice-236",
                "Hyunsu Korean": "voice-384"
            },
            "female": {
                "SunHi": "voice-237"
            }
        },
        "United States": {
            "male": {
                "Andrew Korean": "voice-375",
                "Brian Korean": "voice-377"
            },
            "female": {
                "Ava Korean": "voice-376",
                "Emma Korean": "voice-378"
            }
        },
        "France": {
            "male": {
                "Remy Korean": "voice-379"
            },
            "female": {
                "Vivienne Korean": "voice-380"
            }
        },
        "Germany": {
            "male": {
                "Florian Korean": "voice-381"
            },
            "female": {
                "Seraphina Korean": "voice-382"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Korean": "voice-383"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Korean": "voice-385"
            }
        }
    },
    "Lao": {
        "Laos": {
            "male": {
                "Chanthavong": "voice-238"
            },
            "female": {
                "Keomany": "voice-239"
            }
        }
    },
    "Latvian": {
        "Latvia": {
            "female": {
                "Everita": "voice-240"
            },
            "male": {
                "Nils": "voice-241"
            }
        }
    },
    "Lithuanian": {
        "Lithuania": {
            "male": {
                "Leonas": "voice-242"
            },
            "female": {
                "Ona": "voice-243"
            }
        }
    },
    "Macedonian": {
        "North Macedonia": {
            "male": {
                "Aleksandar": "voice-244"
            },
            "female": {
                "Marija": "voice-245"
            }
        }
    },
    "Malay": {
        "Malaysia": {
            "male": {
                "Osman": "voice-246"
            },
            "female": {
                "Yasmin": "voice-247"
            }
        }
    },
    "Malayalam": {
        "India": {
            "male": {
                "Midhun": "voice-248"
            },
            "female": {
                "Sobhana": "voice-249"
            }
        }
    },
    "Maltese": {
        "Malta": {
            "female": {
                "Grace": "voice-250"
            },
            "male": {
                "Joseph": "voice-251"
            }
        }
    },
    "Marathi": {
        "India": {
            "female": {
                "Aarohi": "voice-252"
            },
            "male": {
                "Manohar": "voice-253"
            }
        }
    },
    "Mongolian": {
        "Mongolia": {
            "male": {
                "Bataa": "voice-254"
            },
            "female": {
                "Yesui": "voice-255"
            }
        }
    },
    "Nepali": {
        "Nepal": {
            "female": {
                "Hemkala": "voice-256"
            },
            "male": {
                "Sagar": "voice-257"
            }
        }
    },
    "Norwegian": {
        "Norway": {
            "male": {
                "Finn": "voice-258"
            },
            "female": {
                "Pernille": "voice-259"
            }
        },
        "United States": {
            "male": {
                "Andrew Norwegian": "voice-463",
                "Brian Norwegian": "voice-465"
            },
            "female": {
                "Ava Norwegian": "voice-464",
                "Emma Norwegian": "voice-466"
            }
        },
        "France": {
            "male": {
                "Remy Norwegian": "voice-467"
            },
            "female": {
                "Vivienne Norwegian": "voice-468"
            }
        },
        "Germany": {
            "male": {
                "Florian Norwegian": "voice-469"
            },
            "female": {
                "Seraphina Norwegian": "voice-470"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Norwegian": "voice-471"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Norwegian": "voice-472"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Norwegian": "voice-473"
            }
        }
    },
    "Pashto": {
        "Afghanistan": {
            "male": {
                "GulNawaz": "voice-260"
            },
            "female": {
                "Latifa": "voice-261"
            }
        }
    },
    "Persian": {
        "Iran": {
            "female": {
                "Dilara": "voice-262"
            },
            "male": {
                "Farid": "voice-263"
            }
        }
    },
    "Polish": {
        "Poland": {
            "male": {
                "Marek": "voice-264"
            },
            "female": {
                "Zofia": "voice-265"
            }
        },
        "United States": {
            "male": {
                "Andrew Polish": "voice-496",
                "Brian Polish": "voice-498"
            },
            "female": {
                "Ava Polish": "voice-497",
                "Emma Polish": "voice-499"
            }
        },
        "France": {
            "male": {
                "Remy Polish": "voice-500"
            },
            "female": {
                "Vivienne Polish": "voice-501"
            }
        },
        "Germany": {
            "male": {
                "Florian Polish": "voice-502"
            },
            "female": {
                "Seraphina Polish": "voice-503"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Polish": "voice-504"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Polish": "voice-505"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Polish": "voice-506"
            }
        }
    },
    "Portuguese": {
        "Brazil": {
            "male": {
                "Antonio": "voice-266"
            },
            "female": {
                "Francisca": "voice-267",
                "Thalita Portuguese": "voice-374"
            }
        },
        "Portugal": {
            "male": {
                "Duarte": "voice-268"
            },
            "female": {
                "Raquel": "voice-269"
            }
        },
        "United States": {
            "male": {
                "Andrew Portuguese": "voice-364",
                "Brian Portuguese": "voice-366"
            },
            "female": {
                "Ava Portuguese": "voice-365",
                "Emma Portuguese": "voice-367"
            }
        },
        "France": {
            "male": {
                "Remy Portuguese": "voice-368"
            },
            "female": {
                "Vivienne Portuguese": "voice-369"
            }
        },
        "Germany": {
            "male": {
                "Florian Portuguese": "voice-370"
            },
            "female": {
                "Seraphina Portuguese": "voice-371"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Portuguese": "voice-372"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Portuguese": "voice-373"
            }
        }
    },
    "Romanian": {
        "Romania": {
            "female": {
                "Alina": "voice-270"
            },
            "male": {
                "Emil": "voice-271"
            }
        },
        "United States": {
            "male": {
                "Andrew Romanian": "voice-507",
                "Brian Romanian": "voice-509"
            },
            "female": {
                "Ava Romanian": "voice-508",
                "Emma Romanian": "voice-510"
            }
        },
        "France": {
            "male": {
                "Remy Romanian": "voice-511"
            },
            "female": {
                "Vivienne Romanian": "voice-512"
            }
        },
        "Germany": {
            "male": {
                "Florian Romanian": "voice-513"
            },
            "female": {
                "Seraphina Romanian": "voice-514"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Romanian": "voice-515"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Romanian": "voice-516"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Romanian": "voice-517"
            }
        }
    },
    "Russian": {
        "Russia": {
            "male": {
                "Dmitry": "voice-272"
            },
            "female": {
                "Svetlana": "voice-273"
            }
        },
        "United States": {
            "male": {
                "Andrew Russian": "voice-430",
                "Brian Russian": "voice-432"
            },
            "female": {
                "Ava Russian": "voice-431",
                "Emma Russian": "voice-433"
            }
        },
        "France": {
            "male": {
                "Remy Russian": "voice-434"
            },
            "female": {
                "Vivienne Russian": "voice-435"
            }
        },
        "Germany": {
            "male": {
                "Florian Russian": "voice-436"
            },
            "female": {
                "Seraphina Russian": "voice-437"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Russian": "voice-438"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Russian": "voice-439"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Russian": "voice-440"
            }
        }
    },
    "Serbian": {
        "Serbia": {
            "male": {
                "Nicholas": "voice-274"
            },
            "female": {
                "Sophie": "voice-275"
            }
        }
    },
    "Sinhala": {
        "Sri Lanka": {
            "male": {
                "Sameera": "voice-276"
            },
            "female": {
                "Thilini": "voice-277"
            }
        }
    },
    "Slovak": {
        "Slovakia": {
            "male": {
                "Lukas": "voice-278"
            },
            "female": {
                "Viktoria": "voice-279"
            }
        }
    },
    "Slovenian": {
        "Slovenia": {
            "female": {
                "Petra": "voice-280"
            },
            "male": {
                "Rok": "voice-281"
            }
        }
    },
    "Somali": {
        "Somalia": {
            "male": {
                "Muuse": "voice-282"
            },
            "female": {
                "Ubax": "voice-283"
            }
        }
    },
    "Sundanese": {
        "Indonesia": {
            "male": {
                "Jajang": "voice-284"
            },
            "female": {
                "Tuti": "voice-285"
            }
        }
    },
    "Swahili": {
        "Kenya": {
            "male": {
                "Rafiki": "voice-286"
            },
            "female": {
                "Zuri": "voice-287"
            }
        },
        "Tanzania": {
            "male": {
                "Daudi": "voice-288"
            },
            "female": {
                "Rehema": "voice-289"
            }
        }
    },
    "Swedish": {
        "Sweden": {
            "male": {
                "Mattias": "voice-290"
            },
            "female": {
                "Sofie": "voice-291"
            }
        },
        "United States": {
            "male": {
                "Andrew Swedish": "voice-452",
                "Brian Swedish": "voice-454"
            },
            "female": {
                "Ava Swedish": "voice-453",
                "Emma Swedish": "voice-455"
            }
        },
        "France": {
            "male": {
                "Remy Swedish": "voice-456"
            },
            "female": {
                "Vivienne Swedish": "voice-457"
            }
        },
        "Germany": {
            "male": {
                "Florian Swedish": "voice-458"
            },
            "female": {
                "Seraphina Swedish": "voice-459"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Swedish": "voice-460"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Swedish": "voice-461"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Swedish": "voice-462"
            }
        }
    },
    "Tamil": {
        "India": {
            "female": {
                "Pallavi": "voice-292"
            },
            "male": {
                "Valluvar": "voice-293"
            }
        },
        "Sri Lanka": {
            "male": {
                "Kumar": "voice-294"
            },
            "female": {
                "Saranya": "voice-295"
            }
        },
        "Malaysia": {
            "female": {
                "Kani": "voice-296"
            },
            "male": {
                "Surya": "voice-297"
            }
        },
        "Singapore": {
            "male": {
                "Anbu": "voice-298"
            },
            "female": {
                "Venba": "voice-299"
            }
        }
    },
    "Telugu": {
        "India": {
            "male": {
                "Mohan": "voice-300"
            },
            "female": {
                "Shruti": "voice-301"
            }
        }
    },
    "Thai": {
        "Thailand": {
            "male": {
                "Niwat": "voice-302"
            },
            "female": {
                "Premwadee": "voice-303"
            }
        }
    },
    "Turkish": {
        "Turkey": {
            "male": {
                "Ahmet": "voice-304"
            },
            "female": {
                "Emel": "voice-305"
            }
        },
        "United States": {
            "male": {
                "Andrew Turkish": "voice-485",
                "Brian Turkish": "voice-487"
            },
            "female": {
                "Ava Turkish": "voice-486",
                "Emma Turkish": "voice-488"
            }
        },
        "France": {
            "male": {
                "Remy Turkish": "voice-489"
            },
            "female": {
                "Vivienne Turkish": "voice-490"
            }
        },
        "Germany": {
            "male": {
                "Florian Turkish": "voice-491"
            },
            "female": {
                "Seraphina Turkish": "voice-492"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Turkish": "voice-493"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Turkish": "voice-494"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Turkish": "voice-495"
            }
        }
    },
    "Ukrainian": {
        "Ukraine": {
            "male": {
                "Ostap": "voice-306"
            },
            "female": {
                "Polina": "voice-307"
            }
        }
    },
    "Urdu": {
        "India": {
            "female": {
                "Gul": "voice-308"
            },
            "male": {
                "Salman": "voice-309"
            }
        },
        "Pakistan": {
            "male": {
                "Asad": "voice-310"
            },
            "female": {
                "Uzma": "voice-311"
            }
        },
        "United States": {
            "male": {
                "Andrew Urdu": "voice-551",
                "Brian Urdu": "voice-553"
            },
            "female": {
                "Ava Urdu": "voice-552",
                "Emma Urdu": "voice-554"
            }
        },
        "France": {
            "male": {
                "Remy Urdu": "voice-555"
            },
            "female": {
                "Vivienne Urdu": "voice-556"
            }
        },
        "Germany": {
            "male": {
                "Florian Urdu": "voice-557"
            },
            "female": {
                "Seraphina Urdu": "voice-558"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Urdu": "voice-559"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Urdu": "voice-560"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Urdu": "voice-561"
            }
        }
    },
    "Uzbek": {
        "Uzbekistan": {
            "female": {
                "Madina": "voice-312"
            },
            "male": {
                "Sardor": "voice-313"
            }
        }
    },
    "Vietnamese": {
        "Vietnam": {
            "female": {
                "HoaiMy": "voice-314"
            },
            "male": {
                "NamMinh": "voice-315"
            }
        }
    },
    "Welsh": {
        "United Kingdom": {
            "male": {
                "Aled": "voice-316"
            },
            "female": {
                "Nia": "voice-317"
            }
        }
    },
    "Zulu": {
        "South Africa": {
            "female": {
                "Thando": "voice-318"
            },
            "male": {
                "Themba": "voice-319"
            }
        }
    },
    "Mexican": {
        "United States": {
            "male": {
                "Andrew Mexican": "voice-573",
                "Brian Mexican": "voice-575"
            },
            "female": {
                "Ava Mexican": "voice-574",
                "Emma Mexican": "voice-576"
            }
        },
        "France": {
            "male": {
                "Remy Mexican": "voice-577"
            },
            "female": {
                "Vivienne Mexican": "voice-578"
            }
        },
        "Germany": {
            "male": {
                "Florian Mexican": "voice-579"
            },
            "female": {
                "Seraphina Mexican": "voice-580"
            }
        },
        "Italy": {
            "male": {
                "Giuseppe Mexican": "voice-581"
            }
        },
        "South Korea": {
            "male": {
                "Hyunsu Mexican": "voice-582"
            }
        },
        "Brazil": {
            "female": {
                "Thalita Mexican": "voice-583"
            }
        }
    }
}
# Recursively display voices in an enumerated format with enhanced information
def display_voices(voices, prefix="", show_ids=False):
    if not voices:
        print_colored("Error: No voices available.", "red")
        return 0

    index = 0
    for key, value in voices.items():
        if isinstance(value, dict):
            new_prefix = f"{prefix}{key} " if prefix else f"{key} "
            count = display_voices(value, new_prefix, show_ids)
            index += count
        else:
            index += 1
            # Format: "1- English UK female Sonia"
            # Optionally show voice ID: "1- English UK female Sonia (voice-35)"
            if show_ids:
                print(f"{index}- {prefix}{key} \033[90m({value})\033[0m")
            else:
                print(f"{index}- {prefix}{key}")
    return index

# Recursively get the selected voice ID based on user input
def get_voice_id(voices, choice, current_index=0):
    for key, value in voices.items():
        if isinstance(value, dict):
            result, current_index = get_voice_id(value, choice, current_index)
            if result:
                return result, current_index
        else:
            current_index += 1
            if current_index == choice:
                return value, current_index
    return None, current_index

# Function to get audio from the server
def get_audio(url, data, headers, cookies=None):
    try:
        json_data = json.dumps(data)
        response = req.post(url, data=json_data, headers=headers, cookies=cookies)
        response.raise_for_status()
        if response.headers.get('Content-Type') == 'audio/mpeg':
            return response.content
        else:
            print_colored(f"Unexpected response format: {response.headers.get('Content-Type')}", "red")
            return None
    except req.exceptions.RequestException as e:
        if e.response:
            print_colored(f"Server response: {e.response.text}", "red")
        print_colored(f"Request failed: {e}", "red")
        return None
    except Exception as e:
        print_colored(f"An unexpected error occurred: {e}", "red")
        return None

# Function to save audio to a file
def save_audio(response, directory, chunk_num):
    if response:
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f"audio_chunk_{chunk_num}.mp3")
        try:
            with open(file_path, 'wb') as f:
                f.write(response)
            print_colored(f"Audio saved to {file_path}", "green")
        except IOError as e:
            print_colored(f"Error saving audio: {e}", "red")
    else:
        print_colored("No audio data to save", "red")

# Function to split text into chunks
def split_text(text, chunk_size=1000):
    if not text:
        print_colored("Error: No text provided to split.", "red")
        return []

    chunks = []
    while len(text) > 0:
        if len(text) <= chunk_size:
            chunks.append(text)
            break
        chunk = text[:chunk_size]
        last_full_stop = chunk.rfind('.')
        last_comma = chunk.rfind(',')
        split_index = last_full_stop if last_full_stop != -1 else last_comma
        if split_index == -1:
            split_index = chunk_size
        else:
            split_index += 1
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip()
    return chunks

# Function to validate text
def validate_text(text):
    return ''.join(char for char in text if ord(char) < 128)

# Function to get multiline input
def get_multiline_input(prompt="Enter your text (type END on a new line when finished):"):
    print_colored(prompt, "cyan")
    print_colored("(Type your text, then press Enter and type END to finish)", "yellow")
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    return " ".join(lines)

# Function to prompt for graceful exit
def prompt_graceful_exit():
    while True:
        choice = input_colored("\nDo you want to exit? (y/n): ", "blue").lower()
        if choice == "y":
            print_colored("Exiting gracefully...", "magenta")
            sys.exit(0)
        elif choice == "n":
            return
        else:
            print_colored("Invalid choice. Please enter 'y' or 'n'.", "red")

# Function to count voices in the hierarchical structure
def count_voice_stats(voices):
    stats = {
        'total': 0,
        'languages': set(),
        'countries': set(),
        'genders': set()
    }

    def count_recursive(data, level=0):
        for key, value in data.items():
            if isinstance(value, dict):
                if level == 0:  # Language level
                    stats['languages'].add(key)
                elif level == 1:  # Country level
                    stats['countries'].add(key)
                elif level == 2:  # Gender level
                    stats['genders'].add(key)
                count_recursive(value, level + 1)
            else:
                stats['total'] += 1

    count_recursive(voices)
    return stats

# Main function
def main():
    voices = load_voices()
    if not voices:
        print_colored("Error: No voices available. Exiting.", "red")
        return

    # Display statistics
    stats = count_voice_stats(voices)
    print_colored("=" * 60, "cyan")
    print_colored("🎤 Speechma Text-to-Speech", "magenta")
    print_colored("=" * 60, "cyan")
    print_colored(f"📊 Voice Library Statistics:", "yellow")
    print(f"   Total Voices: {stats['total']}")
    print(f"   Languages: {len(stats['languages'])} ({', '.join(sorted(stats['languages']))})")
    print(f"   Countries: {len(stats['countries'])} ({', '.join(sorted(stats['countries']))})")
    print(f"   Genders: {len(stats['genders'])} ({', '.join(sorted(stats['genders']))})")
    print_colored("=" * 60, "cyan")

    # Ask if user wants to see voice IDs
    show_ids_input = input_colored("\nShow voice IDs? (y/n, default: n): ", "blue").lower()
    show_ids = show_ids_input == 'y'

    print_colored("\n📋 Available voices:", "blue")
    total_voices = display_voices(voices, show_ids=show_ids)

    try:
        choice = int(input_colored(f"\nEnter the number of the voice you want to use (1-{total_voices}): ", "green"))
        if choice < 1 or choice > total_voices:
            print_colored("Error: Invalid choice. Please enter a valid number.", "red")
            return
    except ValueError:
        print_colored("Error: Invalid input. Please enter a number.", "red")
        return

    voice_id, _ = get_voice_id(voices, choice)
    if not voice_id:
        print_colored("Error: Invalid voice choice. Exiting.", "red")
        return

    text = get_multiline_input().replace("  ", " ")
    
    if not text:
        print_colored("Error: No text provided. Exiting.", "red")
        return
    elif len(text) <= 9 :
        print_colored("Error: The text must be more than 9 characters. Exiting.", "red")
        return

    text = validate_text(text)

    url = 'https://speechma.com/com.api/tts-api.php'
    headers = {
        'Host': 'speechma.com',
        'Sec-Ch-Ua-Platform': 'Windows',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'Content-Type': 'application/json',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36',
        'Accept': '*/*',
        'Origin': 'https://speechma.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://speechma.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Priority': 'u=1, i'
    }

    # IMPORTANT: You need to get cookies from your browser after visiting speechma.com
    # Instructions:
    # 1. Visit https://speechma.com in your browser
    # 2. Complete any CAPTCHA/bot check
    # 3. Open Developer Tools (F12) > Application tab > Cookies > speechma.com
    # 4. Copy the cookie values and add them here
    # Example: cookies = {'cf_clearance': 'your_token_here', '__cfruid': 'your_token_here'}
    cookies = None  # Set this to a dictionary with your cookies to bypass 403 errors

    chunks = split_text(text, chunk_size=1000)
    if not chunks:
        print_colored("Error: Could not split text into chunks. Exiting.", "red")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    directory = os.path.join("audio", timestamp)
    
    for i, chunk in enumerate(chunks, start=1):
        print_colored(f"\nProcessing chunk {i}...", "yellow")
        data = {
            "text": chunk.replace("'", "").replace('"', '').replace("&", "and"),
            "voice": voice_id
        }

        max_retries = 3
        for retry in range(max_retries):
            response = get_audio(url, data, headers, cookies)
            if response:
                save_audio(response, directory, i)
                break
            else:
                print_colored(f"Retry {retry + 1} for chunk {i}...", "yellow")
        else:
            print_colored(f"Failed to process chunk {i} after {max_retries} retries.", "red")

    prompt_graceful_exit()

# Main execution
if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
        sys.exit(0)
