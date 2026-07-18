"""Catalogo oficial de departamentos y municipios de Guatemala.

Fuente: INE/Wikipedia (https://es.wikipedia.org/wiki/Anexo:Municipios_de_Guatemala),
verificado contra los datos del proyecto. "CIUDAD CAPITAL" no es un
departamento oficial: es una particion propia de MINEDUC sobre el municipio
de Guatemala, reportada por zona (ZONA 1..25) en vez de por municipio.

3 valores de MUNICIPIO se dejan deliberadamente fuera del catalogo por no
calzar con ninguna forma oficial (QUEZALTEPEQUE, PACHALUN, SAN MIGUEL PANAM):
ver AvanceProyecto1.md para el detalle y el razonamiento completo.
"""

from __future__ import annotations

from unidecode import unidecode

DEPARTAMENTOS_MUNICIPIOS: dict[str, list[str]] = {
    "Alta Verapaz": [
        "Chahal", "Chisec", "Cobán", "Fray Bartolomé de las Casas",
        "Santa Catalina La Tinta", "Lanquín", "Panzós", "Raxruhá",
        "San Cristóbal Verapaz", "San Juan Chamelco", "San Pedro Carchá",
        "Santa Cruz Verapaz", "Cahabón", "Santa María Cahabón", "Senahú",
        "Tamahú", "Tactic", "Tucurú", "San Miguel Tucurú", "La Tinta",
    ],
    "Baja Verapaz": [
        "Cubulco", "Granados", "Purulhá", "Rabinal", "Salamá", "San Jerónimo",
        "San Miguel Chicaj", "Santa Cruz el Chol",
    ],
    "Chimaltenango": [
        "Acatenango", "Chimaltenango", "El Tejar", "Parramos", "Patzicía",
        "Patzún", "Pochuta", "San Miguel Pochuta", "San Andrés Itzapa",
        "San José Poaquíl", "San Juan Comalapa", "San Martín Jilotepeque",
        "Santa Apolonia", "Santa Cruz Balanyá", "Tecpán", "Tecpán Guatemala",
        "Yepocapa", "San Pedro Yepocapa", "Zaragoza",
    ],
    "Chiquimula": [
        "Camotán", "Chiquimula", "Concepción Las Minas", "Esquipulas", "Ipala",
        "Jocotán", "Olopa", "Quetzaltepeque", "San Jacinto", "San José la Arada",
        "San Juan Ermita",
    ],
    "El Progreso": [
        "El Jícaro", "Guastatoya", "Morazán", "San Agustín Acasaguastlán",
        "San Antonio La Paz", "San Cristóbal Acasaguastlán", "Sanarate", "Sansare",
    ],
    "Escuintla": [
        "Escuintla", "Guanagazapa", "Iztapa", "La Democracia", "La Gomera",
        "Masagua", "Nueva Concepción", "Palín", "San José", "San Vicente Pacaya",
        "Santa Lucía Cotzumalguapa", "Sipacate", "Siquinalá", "Tiquisate",
    ],
    "Guatemala": [
        "Amatitlán", "Chinautla", "Chuarrancho", "Guatemala", "Fraijanes",
        "Mixco", "Palencia", "San José del Golfo", "San José Pinula",
        "San Juan Sacatepéquez", "San Miguel Petapa", "San Pedro Ayampuc",
        "San Pedro Sacatepéquez", "San Raymundo", "Santa Catarina Pinula",
        "Villa Canales", "Villa Nueva",
    ],
    "Huehuetenango": [
        "Aguacatán", "Chiantla", "Colotenango", "Concepción Huista", "Cuilco",
        "Huehuetenango", "Jacaltenango", "La Democracia", "La Libertad",
        "Malacatancito", "Nentón", "Petatán", "San Antonio Huista",
        "San Gaspar Ixchil", "San Ildefonso Ixtahuacán", "San Juan Atitán",
        "San Juan Ixcoy", "San Mateo Ixtatán", "San Miguel Acatán",
        "San Pedro Nectá", "San Pedro Soloma", "San Rafael La Independencia",
        "San Rafael Pétzal", "San Sebastián Coatán", "San Sebastián Huehuetenango",
        "Santa Ana Huista", "Santa Bárbara", "Santa Cruz Barillas",
        "Santa Eulalia", "Santiago Chimaltenango", "Tectitán",
        "Todos Santos Cuchumatán", "Unión Cantinil",
    ],
    "Izabal": ["El Estor", "Livingston", "Los Amates", "Morales", "Puerto Barrios"],
    "Jalapa": [
        "Jalapa", "Mataquescuintla", "Monjas", "San Carlos Alzatate",
        "San Luis Jilotepeque", "San Manuel Chaparrón", "San Pedro Pinula",
    ],
    "Jutiapa": [
        "Agua Blanca", "Asunción Mita", "Atescatempa", "Comapa", "Conguaco",
        "El Adelanto", "El Progreso", "Jalpatagua", "Jerez", "Jutiapa", "Moyuta",
        "Pasaco", "Quesada", "San José Acatempa", "Santa Catarina Mita",
        "Yupiltepeque", "Zapotitlán",
    ],
    "Petén": [
        "Dolores", "El Chal", "Flores", "Santa Elena de la Cruz", "La Libertad",
        "Las Cruces", "Melchor de Mencos", "Poptún", "San Andrés", "San Benito",
        "San Francisco", "San José", "San Luis", "Santa Ana", "Sayaxché",
    ],
    "Quetzaltenango": [
        "Almolonga", "Cabricán", "Cajolá", "Cantel", "Coatepeque",
        "Colomba Costa Cuca", "Concepción Chiquirichapa", "El Palmar",
        "Flores Costa Cuca", "Génova", "Génova Costa Cuca", "Huitán",
        "La Esperanza", "Olintepeque",
        "Palestina de Los Altos", "Quetzaltenango", "Salcajá", "San Carlos Sija",
        "San Francisco La Unión", "San Juan Ostuncalco", "San Martín Sacatepéquez",
        "San Mateo", "San Miguel Sigüilá", "Sibilia", "Zunil",
    ],
    "Quiché": [
        "Canillá", "Chajul", "Chicamán", "Chiché", "Santo Tomás Chichicastenango",
        "Chinique", "Cunén", "Ixcán", "Joyabaj", "Nebaj", "Pachalum", "Patzité",
        "Sacapulas", "San Andrés Sajcabajá", "San Antonio Ilotenango",
        "San Bartolomé Jocotenango", "San Juan Cotzal", "San Pedro Jocopilas",
        "Santa Cruz del Quiché", "Uspantán", "San Miguel Uspantán", "Zacualpa",
    ],
    "Retalhuleu": [
        "Champerico", "El Asintal", "Nuevo San Carlos", "Retalhuleu",
        "San Andrés Villa Seca", "San Felipe", "San Martín Zapotitlán",
        "San Sebastián", "Santa Cruz Muluá",
    ],
    "Sacatepéquez": [
        "Alotenango", "Ciudad Vieja", "Jocotenango", "Antigua Guatemala",
        "Magdalena Milpas Altas", "Pastores", "San Antonio Aguas Calientes",
        "San Bartolomé Milpas Altas", "San Lucas Sacatepéquez",
        "San Miguel Dueñas", "Santa Catarina Barahona", "Santa Lucía Milpas Altas",
        "Santa María de Jesús", "Santiago Sacatepéquez", "Santo Domingo Xenacoj",
        "Sumpango",
    ],
    "San Marcos": [
        "Ayutla", "Catarina", "Comitancillo", "Concepción Tutuapa", "El Quetzal",
        "El Tumbador", "Esquipulas Palo Gordo", "Ixchiguán", "La Blanca",
        "La Reforma", "Malacatán", "Nuevo Progreso", "Ocós", "Pajapita",
        "Río Blanco", "San Antonio Sacatepéquez", "San Cristóbal Cucho",
        "San José El Rodeo", "San José Ojetenam", "San Lorenzo", "San Marcos",
        "San Miguel Ixtahuacán", "San Pablo", "San Pedro Sacatepéquez",
        "San Rafael Pie de la Cuesta", "Sibinal", "Sipacapa", "Tacaná",
        "Tajumulco", "Tejutla",
    ],
    "Santa Rosa": [
        "Barberena", "Casillas", "Chiquimulilla", "Cuilapa", "Guazacapán",
        "Nueva Santa Rosa", "Oratorio", "Pueblo Nuevo Viñas", "San Juan Tecuaco",
        "San Rafael las Flores", "Santa Cruz Naranjo", "Santa María Ixhuatán",
        "Santa Rosa de Lima", "Taxisco",
    ],
    "Sololá": [
        "Concepción", "Nahualá", "Panajachel", "San Andrés Semetabaj",
        "San Antonio Palopó", "San José Chacayá", "San Juan La Laguna",
        "San Lucas Tolimán", "San Marcos La Laguna", "San Pablo La Laguna",
        "San Pedro La Laguna", "Santa Catarina Ixtahuacán",
        "Santa Catarina Palopó", "Santa Clara La Laguna", "Santa Cruz La Laguna",
        "Santa Lucía Utatlán", "Santa María Visitación", "Santiago Atitlán",
        "Sololá",
    ],
    "Suchitepéquez": [
        "Chicacao", "Cuyotenango", "Mazatenango", "Patulul", "Pueblo Nuevo",
        "Río Bravo", "Samayac", "San Antonio Suchitepéquez", "San Bernardino",
        "San Francisco Zapotitlán", "San Gabriel", "San José El Ídolo",
        "San José La Máquina", "San Juan Bautista", "San Lorenzo",
        "San Miguel Panán", "San Pablo Jocopilas", "Santa Bárbara",
        "Santo Domingo Suchitepéquez", "Santo Tomás La Unión", "Zunilito",
    ],
    "Totonicapán": [
        "Momostenango", "San Andrés Xecul", "San Bartolo Aguas Calientes",
        "San Cristóbal Totonicapán", "San Francisco El Alto",
        "Santa Lucía La Reforma", "Santa María Chiquimula", "Totonicapán",
    ],
    "Zacapa": [
        "Cabañas", "Estanzuela", "Gualán", "Huité", "La Unión", "Río Hondo",
        "San Diego", "San Jorge", "Teculután", "Usumatlán", "Zacapa",
    ],
}

# Nombres oficiales con tilde para presentacion (clave = version sin tilde en
# mayusculas, tal como se usa para las comparaciones internas).
DEPARTAMENTOS_CANONICOS = {
    "PETEN": "PETÉN",
    "QUICHE": "QUICHÉ",
    "SACATEPEQUEZ": "SACATEPÉQUEZ",
    "SOLOLA": "SOLOLÁ",
    "SUCHITEPEQUEZ": "SUCHITEPÉQUEZ",
    "TOTONICAPAN": "TOTONICAPÁN",
}

# "Ciudad Capital" no es un departamento oficial de Guatemala: es una
# particion administrativa propia de MINEDUC sobre el municipio de Guatemala,
# reportada por zona en vez de por municipio.
DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL = "CIUDAD CAPITAL"
ZONAS_CIUDAD_CAPITAL_VALIDAS = {f"ZONA {i}" for i in range(1, 26)}


def _clave(texto: str) -> str:
    return unidecode(texto).strip().upper()


def departamento_canonico(valor: str) -> str:
    clave = _clave(valor)
    if clave == DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL:
        return DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL
    return DEPARTAMENTOS_CANONICOS.get(clave, clave)


def departamento_valido(valor: str) -> bool:
    clave = _clave(valor)
    if clave == DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL:
        return True
    return clave in {_clave(d) for d in DEPARTAMENTOS_MUNICIPIOS}


_MUNICIPIOS_POR_DEPTO_CLAVE: dict[str, dict[str, str]] = {
    _clave(depto): {_clave(m): m.upper() for m in municipios}
    for depto, municipios in DEPARTAMENTOS_MUNICIPIOS.items()
}


def municipio_canonico(departamento: str, municipio: str) -> str:
    """Devuelve el nombre de municipio normalizado (mayusculas, con tilde
    cuando el catalogo oficial la tiene). Si no se reconoce, regresa el valor
    de entrada normalizado en mayusculas sin alterar su contenido."""
    depto_clave = _clave(departamento)
    if depto_clave == DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL:
        return municipio.strip().upper()
    catalogo = _MUNICIPIOS_POR_DEPTO_CLAVE.get(depto_clave, {})
    return catalogo.get(_clave(municipio), municipio.strip().upper())


def municipio_valido(departamento: str, municipio: str) -> bool:
    depto_clave = _clave(departamento)
    muni_clave = _clave(municipio)
    if depto_clave == DEPARTAMENTO_ESPECIAL_CIUDAD_CAPITAL:
        return municipio.strip().upper() in ZONAS_CIUDAD_CAPITAL_VALIDAS
    catalogo = _MUNICIPIOS_POR_DEPTO_CLAVE.get(depto_clave)
    if catalogo is None:
        return False
    return muni_clave in catalogo
