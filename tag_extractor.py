
KNOWN_TAGS = {
    "ecommerce": ["checkout", "carrello", "ordine", "pagamento", "spedizione"],
    "magazzino": ["stock", "inventario", "giacenza", "magazzino"],
    "gestionale": ["gestion", "erp", "db", "database"],
    "marketing": ["banner", "promo", "promozione", "campagna"],
    "frontend": ["css", "html", "interfaccia"],
    "backend": ["api", "server", "errore 500", "timeout"],
    "assistenzaclienti": ["cliente", "richiesta", "assistenza"],
}



def extract_tags(description: str):
    if not description:
        return []

    desc = description.lower()
    extracted = []

    for tag, keywords in KNOWN_TAGS.items():
        for kw in keywords:
            if kw in desc:
                extracted.append(tag)

    return extracted