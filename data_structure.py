from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Announcement:
    """Rappresenta un singolo annuncio per una provincia."""
    province_code: str
    links: List[str] = field(default_factory=list)
    
    def add_link(self, link: str) -> None:
        """Aggiunge un link alla lista."""
        self.links.append(link)
    
    def remove_link(self, link: str) -> bool:
        """Rimuove un link dalla lista. Restituisce True se trovato."""
        if link in self.links:
            self.links.remove(link)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario."""
        return {
            "province_code": self.province_code,
            "links": self.links.copy()
        }


@dataclass
class ClassResult:
    """Rappresenta un risultato per una classe di concorso."""
    class_code: str
    announcements: List[Announcement] = field(default_factory=list)
    
    def add_announcement(self, province_code: str, links: Optional[List[str]] = None) -> Announcement:
        """Aggiunge o recupera un annuncio per una provincia."""
        # Cerca se esiste già un annuncio per questa provincia
        existing = self.get_announcement_by_province(province_code)
        if existing:
            return existing
        
        # Crea nuovo annuncio
        announcement = Announcement(
            province_code=province_code,
            links=links or []
        )
        self.announcements.append(announcement)
        return announcement
    
    def get_announcement_by_province(self, province_code: str) -> Optional[Announcement]:
        """Recupera un annuncio per codice provincia."""
        for ann in self.announcements:
            if ann.province_code == province_code:
                return ann
        return None
    
    
    
    def remove_announcement(self, province_code: str) -> bool:
        """Rimuove un annuncio per provincia. Restituisce True se trovato."""
        ann = self.get_announcement_by_province(province_code)
        if ann:
            self.announcements.remove(ann)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario."""
        return {
            "class_code": self.class_code,
            "announcements": [ann.to_dict() for ann in self.announcements]
        }


@dataclass
class ResultsContainer:
    """Contenitore principale per tutti i risultati."""
    results: List[ClassResult] = field(default_factory=list)
    
    def add_result(self, class_code: str) -> ClassResult:
        """Aggiunge o recupera un risultato per una classe di concorso."""
        # Cerca se esiste già
        existing = self.get_result_by_class(class_code)
        if existing:
            return existing
        
        # Crea nuovo risultato
        result = ClassResult(class_code=class_code)
        self.results.append(result)
        return result
    
    def get_result_by_class(self, class_code: str) -> Optional[ClassResult]:
        """Recupera un risultato per codice classe."""
        for res in self.results:
            if res.class_code == class_code:
                return res
        return None
    
    def remove_result(self, class_code: str) -> bool:
        """Rimuove un risultato per classe. Restituisce True se trovato."""
        res = self.get_result_by_class(class_code)
        if res:
            self.results.remove(res)
            return True
        return False
    
    def add_link(self, class_code: str, province_code: str, link: str) -> None:
        """Aggiunge un link a una specifica classe e provincia."""
        result = self.get_result_by_class(class_code)
        if not result:
            result = self.add_result(class_code)
        
        announcement = result.get_announcement_by_province(province_code)
        if not announcement:
            announcement = result.add_announcement(province_code)
        
        announcement.add_link(link)
    
    def get_links(self, class_code: str, province_code: str) -> List[str]:
        """Recupera tutti i link per una classe e provincia."""
        result = self.get_result_by_class(class_code)
        if not result:
            return []
        
        announcement = result.get_announcement_by_province(province_code)
        if not announcement:
            return []
        
        return announcement.links.copy()
    
    def get_new_links(self, class_code: str, province_code: str, candidate_links: List[str]) -> List[str]:
        """Restituisce solo i link nuovi rispetto a quelli già presenti per classe e provincia."""
        existing_links = set(self.get_links(class_code, province_code))
        return [link for link in candidate_links if link not in existing_links]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte l'intera struttura in dizionario."""
        return {
            "results": [res.to_dict() for res in self.results]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Converte in stringa JSON formattata."""
        import json
        return json.dumps(self.to_dict(), indent=indent)
    
    def __has_any_links(self) -> bool:
        """Restituisce True se c'è almeno un link in tutto il container."""
        for result in self.results:
            for announcement in result.announcements:
                if announcement.links:  # Lista non vuota
                    return True
        return False
    
    def count_links(self) -> int:
        """Restituisce il numero di link totali dell'oggetto"""
        return sum(len(announcement.links) for result in self.results 
                                      for announcement in result.announcements)
    
    def get_tg_message(self) -> str:
        """Genera il messaggio da mandare tramite bot telegram"""
        tg_message = ""
        if self.__has_any_links():
            tg_message = "Nuovi interpelli trovati! ecco i link!\n"
        for res in self.results:
            tg_message += f"-Per la classe di concorso {res.class_code}\n"
            for ann in res.announcements:
                tg_message += f"--Provincia {ann.province_code} link: \n"
                for link in ann.links:
                    tg_message += f"{link}\n"

        return tg_message


    @classmethod
    def from_json(cls, json_string: str) -> 'ResultsContainer':
        """Crea un'istanza da una stringa JSON."""
        import json
        data = json.loads(json_string)
        return cls.from_dict(data)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResultsContainer':
        """Crea un'istanza da un dizionario."""
        container = cls()
        
        for res_data in data.get("results", []):
            result = container.add_result(res_data["class_code"])
            
            for ann_data in res_data.get("announcements", []):
                announcement = result.add_announcement(
                    province_code=ann_data["province_code"],
                    links=ann_data.get("links", [])
                )
        
        return container


# Esempio di utilizzo
if __name__ == "__main__":
    # Creazione da zero
    container = ResultsContainer()
    
    # Aggiunta dati
    container.add_link("A041", "IM", "linkTest")
    container.add_link("A041", "IM", "link2")
    container.add_link("A041", "SV", "linkTestSV")
    container.add_link("A041", "SV", "link2SV")
    container.add_link("A040", "IM", "linkTest")
    container.add_link("A040", "IM", "link2")
    container.add_link("A042", "IM", "linkTest")
    
    # Stampa come JSON
    print("Struttura JSON:")
    print(container.to_json())
    
    # Recupero dati
    print("\nLink per A041 - IM:")
    print(container.get_links("A041", "IM"))
    
    # Creazione da dizionario esistente
    sample_data = {
        "results": [
            {
                "class_code": "A041",
                "announcements": [
                    {
                        "province_code": "IM",
                        "links": ["linkTest", "link2"]
                    },
                    {
                        "province_code": "SV",
                        "links": ["linkTestSV", "link2SV"]
                    }
                ]
            }
        ]
    }
    
    container_from_dict = ResultsContainer.from_dict(sample_data)
    print("\nCreato da dizionario:")
    print(container_from_dict.to_json())