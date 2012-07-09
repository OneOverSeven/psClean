# coding=utf8
############################
## Author: Mark Huberty, Mimi Tam, and Georg Zachmann
## Date Begun: 23 May 2012
## Purpose: Module to clean inventor / assignee data in the PATSTAT patent
##          database
## License: BSD Simplified
## Copyright (c) 2012, Authors
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## 
## 1. Redistributions of source code must retain the above copyright notice, this
##    list of conditions and the following disclaimer. 
## 2. Redistributions in binary form must reproduce the above copyright notice,
##    this list of conditions and the following disclaimer in the documentation
##    and/or other materials provided with the distribution. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
## 
## The views and conclusions contained in the software and documentation are those
## of the authors and should not be interpreted as representing official policies, 
## either expressed or implied, of the FreeBSD Project.
############################

import re
import unicodedata

##Some subfunction stubs
def stdize_case(string): 
    """
    Small function to standardize case using built-in string function.
    Args:
        string
    Returns:
        returns the uppercase of input string
    """
    result = string.upper()
    return result

def rem_diacritics(string):
    """
    Small function to remove diacritics/accents by converting to unicode.
    Args:
        string
    Returns:
        returns the input string with the diacritics/accents removed
    """
    
    #Don't need following line if we are using unicode data already
    #s = unicode(string)
    result = ''.join((c for c in unicodedata.normalize('NFD',s) if
                      unicodedata.category(c) !='Mn'))
    return result

def rem_trail_spaces(string):
    """
    Small function to remove trailing spaces with built-in strip function.
    Args:
        string
    Returns:
        returns the input string with trailing spaces removed
    """
    s = string.strip()
    return s

#a sort of main function
def master_clean_dicts(input_string_list, cleanup_dicts):
    """
    Checks each string in an list and does a find/replace based on
    values in a list of replace:find dicts
    
    Args:
        input_string_list: string to be cleaned
        cleanup_dicts: list of dicts to be used on the input string.
        Dicts should be replace:find where find is either a string or
        a list of strings
    Returns:
    A list of cleaned strings of same length as input_string_list
    """
    regex_dicts = [make_regex(d) for d in cleanup_dicts]
    
    for i, s in enumerate(input_string_list):
        for cleanup_dict in regex_dicts:
            s = mult_replace(s, cleanup_dict)
        input_string_list[i] = s
    return input_string_list  

def mult_replace(input_string, regex_dict):
    """
    Small function to replace input_string with different values using a
    a regex_dict.
    Args:
        input_string: string to be cleaned
        regex_dict: dict of regular expressions used to clean the input_string 
    Returns:
        output_string: cleaned string (using the regex_dict)
    """
    output_string = input_string
    for k, v in regex_dict.iteritems():
        output_string = v.sub(k, output_string)
    return output_string

def make_regex(input_dict):
    """
    Small function to create a regex_dict from an input dict of regular expressions
    Args:
        input_dict: dict of regular expressions to be compiled
    Returns:
        regex_dict: dict of compiled regular expressions
    """
    regex_dict = {}
    for k, v in input_dict.iteritems():
        if isinstance(v, str):
            regex_dict[k] = re.compile(v)
        elif isinstance(v, list):
            expression = '|'.join(v)
            regex_dict[k] = re.compile(expression)
        else:
            raise Exception('Invalid input type!')## Throw an error
    return regex_dict

def get_dicts():
    return [convert_html,
            convert_sgml,
            clean_symbols,
            concatenators,
            single_space,
            ampersand,
            us_uk,
            abbreviations
            ]

def encoder(v):
    """
    Small function to encode only the strings to UTF-8.
    Used mainly to convert items in rows to utf-8 before being written to
    csv by csv.writer which does not accept unicode.
    Args:
        v: any type
    Returns:
        v as utf-8 if it was unicode, otherwise return v
    Usage(in context of rows):
        for row in results:
            writer.writerow(tuple(encoder(v) for i,v in enumerate(row)))
    """
    if isinstance(v,unicode):
        return v.encode('utf-8')
    else:
        return v

def decoder(v,encoding='utf-8'):
    """
    Small function to decode for csv reader. Needed to not decode longs.
    Args:
        v: utf-8
    Returns:
        v as unicode if it was utf-8, otherwise return v
    Usage (in context of a csv reader):
        for row in reader:
            decoded.append([decoder(cell) for cell in row])
    """
    if isinstance(v,basestring):
        if not isinstance(v,unicode):
            return unicode(v,encoding)

#Dictionaries used for cleaning
#IMPORTANT NOTE: These all assume that case standardization has already been performed!

#Get rid of HTML tags. For extendability using dictionary. However, per Magerman et al 2006, only HTML tags were <BR>, we should validate  
convert_html = {
    ' ': r'<\s*BR\s*>' #break 
    }

#Get rid of SGML tags as we are getting rid of all symbols. per Magerman Et al, there were only 7 SGML tags found in the OCT 2011 dataset
convert_sgml = {
    '': r'&AMP;|&OACUTE;|&SECT;|&UACUTE;|&#8902;|&BULL;|&EXCL;'
    }

#Remove all non alphanumeric
clean_symbols = {
    '': r'[^\s\w\-\.,;]'
    }

concatenators = {
    ' ': r'[\-\.,;]' #treat -s specially as whitespaces (can be changed later)
    }

#spaces must be single
single_space = {
    ' ':r'\s+' 
    }

#translate all "ands" to other languages... for a more sophisticated version, we should use country codes because it can be dangerous to delete some of the shorter ones such as "I"...
#using groups (?<=\s) as if we don't then consumes a space and then case: " AND AND " will not be matched in one try as the first match will consume the whitespace of the second one
ampersand = {
    '&' : [r'(?<=\s)AND(?=\s)',
           r'(?<=\s)EN(?=\s)',
           r'(?<=\s)DHE(?=\s)',
           r'(?<=\s)və(?=\s)',
           r'(?<=\s)ETA(?=\s)',
           r'(?<=\s)I(?=\s)',
           r'(?<=\s)и(?=\s)',
           r'(?<=\s)A(?=\s)',
           r'(?<=\s)OG(?=\s)',
           r'(?<=\s)KAJ(?=\s)',
           r'(?<=\s)JA(?=\s)',
           r'(?<=\s)AT(?=\s)',
           r'(?<=\s)ET(?=\s)',
           r'(?<=\s)E(?=\s)',
           r'(?<=\s)UND(?=\s)',
           r'(?<=\s)AK(?=\s)',
           r'(?<=\s)ES(?=\s)',
           r'(?<=\s)DAN(?=\s)',
           r'(?<=\s)AGUS(?=\s)',
           r'(?<=\s)UN(?=\s)',
           r'(?<=\s)IR(?=\s)',
           r'(?<=\s)U\s',
           r'(?<=\s)SI(?=\s)',
           r'(?<=\s)IN(?=\s)',
           r'(?<=\s)Y(?=\s)',
           r'(?<=\s)NA(?=\s)',
           r'(?<=\s)OCH(?=\s)',
           r'(?<=\s)VE(?=\s)',
           r'(?<=\s)VA(?=\s)',
           r'(?<=\s)SAMT(?=\s)'
           ] 
    }

#Common US Spellings replaced with UK Spellings
us_uk = {
    'ANALYSE': r'ANALYZE(?=[SD]?)',
    'ARMOUR': r'ARMOR(?=S?|ED?)',
    'COLOUR': r'COLOR(?=S?|[ED]?)',
    'FLUIDISE': r'FLUIDIZE(?=[SD]?)',
    'IMMOBILISE': r'IMMOBILIZE(?=[SD]?)',
    'IONISE': r'IONIZE(?=[SD]?)',
    'MOULD': r'MOLD(?=S?|ED?)',
    'POLARISE': r'POLARIZE(?=[SD]?)',
    'POLYMERISE': r'POLYMERIZE(?=[SD]?)',
    'UNAUTHORISE': r'UNAUTHORIZE(?=[SD]?)',
    'CENTRE': r'CENTER(?=[SD]?)',
    'LANDMINE': r'LAND MINE(?=[SD]?)',
    'MITRE': r'MITER(?=[SD]?)',
    'POLYMERISABLE': r'POLYMERIZABLE(?=[SD]?)',
    'PROGRAMME': r'PROGRAM(?=[SD]?)',
    'THEATRE': r'THEATER(?=[SD]?)',
    'TYRE': r'TIRE(?=[SD]?)',
    'ANAESTHETISING': r'ANESTHETIZING(?=[SD]?)',
    'ANALYSING': r'ANALYZING(?=[SD]?)',
    'ANODISING': r'ANODIZING(?=[SD]?)',
    'ARMOURING': r'ARMORING(?=[SD]?)',
    'ATOMISING': r'ATOMIZING(?=[SD]?)',
    'CAUTERISING': r'CAUTERIZING(?=[SD]?)',
    'CENTRING': r'CENTERING(?=[SD]?)',
    'COLOURING': r'COLORING(?=[SD]?)',
    'CROSSLINKING': r'CROSS-LINKING(?=[SD]?)',
    'CRYSTALLISING': r'CRYSTALLIZING(?=[SD]?)',
    'DECOLOURISING': r'DECOLORIZING(?=[SD]?)',
    'DEMAGNETISING': r'DEMAGNETIZING(?=[SD]?)',
    'DEODORISING': r'DEODORIZING(?=[SD]?)',
    'DEPOLARISING': r'DEPOLARIZING(?=[SD]?)',
    'DEPOLYMERISING': r'DEPOLYMERIZING(?=[SD]?)',
    'DESULFURISING': r'DESULFURIZING(?=[SD]?)',
    'EQUALISING': r'EQUALIZING(?=[SD]?)',
    'FERTILISING': r'FERTILIZING(?=[SD]?)',
    'FLAVOURING': r'FLAVORING(?=[SD]?)',
    'FLUIDISING': r'FLUIDIZING(?=[SD]?)',
    'GALVANISING': r'GALVANIZING(?=[SD]?)',
    'GRAPHITISING': r'GRAPHITIZING(?=[SD]?)',
    'HOMOGENISING': r'HOMOGENIZING(?=[SD]?)',
    'IMMUNISING': r'IMMUNIZING(?=[SD]?)',
    'ISOMERISING': r'ISOMERIZING(?=[SD]?)',
    'LOCALISING': r'LOCALIZING(?=[SD]?)',
    'MAGNETISING': r'MAGNETIZING(?=[SD]?)',
    'MALLEABILISING': r'MALLEABLEIZING(?=[SD]?)',
    'MANOEUVRING': r'MANEUVERING(?=[SD]?)',
    'MERCERISING': r'MERCERIZING(?=[SD]?)',
    'METALLISING': r'METALIZING(?=[SD]?)',
    'MINIMISING': r'MINIMIZING(?=[SD]?)',
    'MOULDING': r'MOLDING(?=[SD]?)',
    'NEUTRALISING': r'NEUTRALIZING(?=[SD]?)',
    'OXIDISING': r'OXIDIZING(?=[SD]?)',
    'OZONISING': r'OZONIZING(?=[SD]?)',
    'PASTEURISING': r'PASTEURIZING(?=[SD]?)',
    'PLOUGHING': r'PLOWING(?=[SD]?)',
    'PRACTISING': r'PRACTICING(?=[SD]?)',
    'PULVERISING': r'PULVERIZING(?=[SD]?)',
    'RECOGNISING': r'RECOGNIZING(?=[SD]?)',
    'SENSITISING': r'SENSITIZING(?=[SD]?)',
    'SUBSIDISING': r'SUBSIDIZING(?=[SD]?)',
    'SYNTHESISING': r'SYNTHESIZING(?=[SD]?)',
    'TABLETTING': r'TABLETING(?=[SD]?)',
    'VULCANISING': r'VULCANIZING(?=[SD]?)',
    'TORCH': r'FLASHLIGHT(?=[SD]?)',
    'PETROL': r'GASOLINE(?=[SD]?)',
    'ALUMINIUM': r'ALUMINUM(?=[SD]?)',
    'CARBONISATION': r'CARBONIZATION(?=[SD]?)',
    'CAUTERISATION': r'CAUTERIZATION(?=[SD]?)',
    'CYCLISATION': r'CYCLIZATION(?=[SD]?)',
    'FERTILISATION': r'FERTILIZATION(?=[SD]?)',
    'IONISATION': r'IONIZATION(?=[SD]?)',
    'MAGNETISATION': r'MAGNETIZATION(?=[SD]?)',
    'MINERALISATION': r'MINERALIZATION(?=[SD]?)',
    'NEUTRALISATION': r'NEUTRALIZATION(?=[SD]?)',
    'OPTIMISATION': r'OPTIMIZATION(?=[SD]?)',
    'POLARISATION': r'POLARIZATION(?=[SD]?)',
    'STERILISATION': r'STERILIZATION(?=[SD]?)',
    'SYNCHRONISATION': r'SYNCHRONIZATION(?=[SD]?)',
    'ARMOUR': r'ARMOR(?=[SD]?)',
    'COLOUR': r'COLOR(?=[SD]?)',
    'FERTILISER': r'FERTILIZER(?=[SD]?)',
    'HARBOUR': r'HARBOR(?=[SD]?)',
    'MULTICOLOUR': r'MULTICOLOR(?=[SD]?)',
    'ODOUR': r'ODOR(?=[SD]?)',
    'PARLOUR': r'PARLOR(?=[SD]?)',
    'SULPHUR': r'SULFUR(?=[SD]?)',
    'VAPOUR': r'VAPOR(?=[SD]?)',
    'AEROPLANE': r'AIRPLANE(?=[SD]?)',
    'ANAESTHETIC': r'ANESTHETIC(?=[SD]?)',
    'ANALYSER': r'ANALYZER(?=[SD]?)',
    'ATOMISER': r'ATOMIZER(?=[SD]?)',
    'CALIBRE': r'CALIBER(?=[SD]?)',
    'CALLIPER': r'CALIPER(?=[SD]?)',
    'CARBURETTOR': r'CARBURETOR(?=[SD]?)',
    'CENTRE': r'CENTER(?=[SD]?)',
    'DESENSITISER': r'DESENSITIZER(?=[SD]?)',
    'DOWNPIPE': r'DOWNSPOUT(?=[SD]?)',
    'DYKE': r'DIKE(?=[SD]?)',
    'ECONOMISER': r'ECONOMIZER(?=[SD]?)',
    'ENCYCLOPAEDIA': r'ENCYCLOPEDIA(?=[SD]?)',
    'FIBREGLASS': r'FIBERGLASS(?=ES?)',
    'FIBRE': r'FIBER(?=[SD]?)',
    'HAEMORRHOID': r'HEMORRHOID(?=[SD]?)',
    'MACHETE': r'MATCHETE(?=[SD]?)',
    'METACENTRE': r'METACENTER(?=[SD]?)',
    'MOLLUSC': r'MOLLUSK(?=[SD]?)',
    'MOULD': r'MOLD(?=[SD]?)',
    'NEBULISER': r'NEBULIZER(?=[SD]?)',
    'PLASTICISER': r'PLASTICIZER(?=[SD]?)',
    'PYJAMA': r'PAJAMA(?=[SD]?)',
    'SECATEUR': r'PRUNING SHEAR(?=[SD]?)',
    'SELVEDGE': r'SELVAGE(?=[SD]?)',
    'STABILISER': r'STABILIZER(?=[SD]?)',
    'SULPHATE': r'SULFATE(?=[SD]?)',
    'SULPHITE': r'SULFITE(?=[SD]?)',
    'TRAM': r'STREETCAR(?=[SD]?)',
    'VAPORISER': r'VAPORIZER(?=[SD]?)',
    'WINDSCREEN': r'WINDSHIELD(?=[SD]?)',
    'BISCUIT': r'COOKIE(?=[SD]?)',
    'LIFT': r'ELEVATOR(?=[SD]?)',
    'GYNAECOLOGY': r'GYNECOLOGY(?=[SD]?)',
    'JEWELLERY': r'JEWELRY(?=[SD]?)',
    'NAPPY': r'DIAPER(?=[SD]?)'
    }

#Common UK Spellings replaced with US Spellings
uk_us = {
    'ANALYZE': r'ANALYSE(?=[DS]?)',
    'ARMOR': r'ARMOUR(?=[S]?|ED?)',
    'COLOR': r'COLOUR(?=[S]?|ED?)',
    'FLUIDIZE': r'FLUIDISE(?=[DS]?)',
    'IMMOBILIZE': r'IMMOBILISE(?=[DS]?)',
    'IONIZE': r'IONISE(?=[DS]?)',
    'MOLD': r'MOULD(?=[S]?|ED?)',
    'POLARIZE': r'POLARISE(?=S?)',
    'POLYMERIZE': r'POLYMERISE(?=S?)',
    'UNAUTHORIZE': r'UNAUTHORISE(?=S?)',
    'CENTER': r'CENTRE(?=S?)',
    'LAND MINE': r'LANDMINE(?=S?)',
    'MITER': r'MITRE(?=S?)',
    'POLYMERIZABLE': r'POLYMERISABLE(?=S?)',
    'PROGRAM': r'PROGRAMME(?=S?)',
    'THEATER': r'THEATRE(?=S?)',
    'TIRE': r'TYRE(?=S?)',
    'ANESTHETIZING': r'ANAESTHETISING(?=S?)',
    'ANALYZING': r'ANALYSING(?=S?)',
    'ANODIZING': r'ANODISING(?=S?)',
    'ARMORING': r'ARMOURING(?=S?)',
    'ATOMIZING': r'ATOMISING(?=S?)',
    'CAUTERIZING': r'CAUTERISING(?=S?)',
    'CENTERING': r'CENTRING(?=S?)',
    'COLORING': r'COLOURING(?=S?)',
    'CROSS-LINKING': r'CROSSLINKING(?=S?)',
    'CRYSTALLIZING': r'CRYSTALLISING(?=S?)',
    'DECOLORIZING': r'DECOLOURISING(?=S?)',
    'DEMAGNETIZING': r'DEMAGNETISING(?=S?)',
    'DEODORIZING': r'DEODORISING(?=S?)',
    'DEPOLARIZING': r'DEPOLARISING(?=S?)',
    'DEPOLYMERIZING': r'DEPOLYMERISING(?=S?)',
    'DESULFURIZING': r'DESULFURISING(?=S?)',
    'EQUALIZING': r'EQUALISING(?=S?)',
    'FERTILIZING': r'FERTILISING(?=S?)',
    'FLAVORING': r'FLAVOURING(?=S?)',
    'FLUIDIZING': r'FLUIDISING(?=S?)',
    'GALVANIZING': r'GALVANISING(?=S?)',
    'GRAPHITIZING': r'GRAPHITISING(?=S?)',
    'HOMOGENIZING': r'HOMOGENISING(?=S?)',
    'IMMUNIZING': r'IMMUNISING(?=S?)',
    'ISOMERIZING': r'ISOMERISING(?=S?)',
    'LOCALIZING': r'LOCALISING(?=S?)',
    'MAGNETIZING': r'MAGNETISING(?=S?)',
    'MALLEABLEIZING': r'MALLEABILISING(?=S?)',
    'MANEUVERING': r'MANOEUVRING(?=S?)',
    'MERCERIZING': r'MERCERISING(?=S?)',
    'METALIZING': r'METALLISING(?=S?)',
    'MINIMIZING': r'MINIMISING(?=S?)',
    'MOLDING': r'MOULDING(?=S?)',
    'NEUTRALIZING': r'NEUTRALISING(?=S?)',
    'OXIDIZING': r'OXIDISING(?=S?)',
    'OZONIZING': r'OZONISING(?=S?)',
    'PASTEURIZING': r'PASTEURISING(?=S?)',
    'PLOWING': r'PLOUGHING(?=S?)',
    'PRACTICING': r'PRACTISING(?=S?)',
    'PULVERIZING': r'PULVERISING(?=S?)',
    'RECOGNIZING': r'RECOGNISING(?=S?)',
    'SENSITIZING': r'SENSITISING(?=S?)',
    'SUBSIDIZING': r'SUBSIDISING(?=S?)',
    'SYNTHESIZING': r'SYNTHESISING(?=S?)',
    'TABLETING': r'TABLETTING(?=S?)',
    'VULCANIZING': r'VULCANISING(?=S?)',
    'FLASHLIGHT': r'TORCH(?=S?)',
    'GASOLINE': r'PETROL(?=S?)',
    'ALUMINUM': r'ALUMINIUM(?=S?)',
    'CARBONIZATION': r'CARBONISATION(?=S?)',
    'CAUTERIZATION': r'CAUTERISATION(?=S?)',
    'CYCLIZATION': r'CYCLISATION(?=S?)',
    'FERTILIZATION': r'FERTILISATION(?=S?)',
    'IONIZATION': r'IONISATION(?=S?)',
    'MAGNETIZATION': r'MAGNETISATION(?=S?)',
    'MINERALIZATION': r'MINERALISATION(?=S?)',
    'NEUTRALIZATION': r'NEUTRALISATION(?=S?)',
    'OPTIMIZATION': r'OPTIMISATION(?=S?)',
    'POLARIZATION': r'POLARISATION(?=S?)',
    'STERILIZATION': r'STERILISATION(?=S?)',
    'SYNCHRONIZATION': r'SYNCHRONISATION(?=S?)',
    'ARMOR': r'ARMOUR(?=S?)',
    'COLOR': r'COLOUR(?=S?)',
    'FERTILIZER': r'FERTILISER(?=S?)',
    'HARBOR': r'HARBOUR(?=S?)',
    'MULTICOLOR': r'MULTICOLOUR(?=S?)',
    'ODOR': r'ODOUR(?=S?)',
    'PARLOR': r'PARLOUR(?=S?)',
    'SULFUR': r'SULPHUR(?=S?)',
    'VAPOR': r'VAPOUR(?=S?)',
    'AIRPLANE': r'AEROPLANE(?=S?)',
    'ANESTHETIC': r'ANAESTHETIC(?=S?)',
    'ANALYZER': r'ANALYSER(?=S?)',
    'ATOMIZER': r'ATOMISER(?=S?)',
    'CALIBER': r'CALIBRE(?=S?)',
    'CALIPER': r'CALLIPER(?=S?)',
    'CARBURETOR': r'CARBURETTOR(?=S?)',
    'CENTER': r'CENTRE(?=S?)',
    'DESENSITIZER': r'DESENSITISER(?=S?)',
    'DOWNSPOUT': r'DOWNPIPE(?=S?)',
    'DIKE': r'DYKE(?=S?)',
    'ECONOMIZER': r'ECONOMISER(?=S?)',
    'ENCYCLOPEDIA': r'ENCYCLOPAEDIA(?=S?)',
    'FIBERGLASS': r'FIBREGLASS(?=S?)',
    'FIBER': r'FIBRE(?=S?)',
    'HEMORRHOID': r'HAEMORRHOID(?=S?)',
    'MATCHETE': r'MACHETE(?=S?)',
    'METACENTER': r'METACENTRE(?=S?)',
    'MOLLUSK': r'MOLLUSC(?=S?)',
    'MOLD': r'MOULD(?=S?)',
    'NEBULIZER': r'NEBULISER(?=S?)',
    'PLASTICIZER': r'PLASTICISER(?=S?)',
    'PAJAMA': r'PYJAMA(?=S?)',
    'PRUNING SHEAR': r'SECATEUR(?=S?)',
    'SELVAGE': r'SELVEDGE(?=S?)',
    'STABILIZER': r'STABILISER(?=S?)',
    'SULFATE': r'SULPHATE(?=S?)',
    'SULFITE': r'SULPHITE(?=S?)',
    'STREETCAR': r'TRAM(?=S?)',
    'VAPORIZER': r'VAPORISER(?=S?)',
    'WINDSHIELD': r'WINDSCREEN(?=S?)',
    'COOKIE': r'BISCUIT(?=S?)',
    'ELEVATOR': r'LIFT(?=S?)',
    'GYNECOLOGY': r'GYNAECOLOGY(?=S?)',
    'JEWELRY': r'JEWELLERY(?=S?)',
    'DIAPER': r'NAPPY(?=S?)'
    }

#Common abbreviations                           
abbreviations = {
    'MIJ': r'MAATSCHAPPIJ',
    'MIN': r'MINISTERIUM|MINISTERSTVA|MINISTERSTWO|MINISTERSTVAM|MINISTERSTVO'
    '|MINISTERSTV|MINISTERO|MINISTERSTVU|MINISTERE|MINISTERUL|MINISTRY|MINISTERSTVE'
    '|MINISTER|MINISTERSTVOM|MINISTRE|MINISTERSTVAKH|MINISTERSTVAMI',
    'PREL': r'PRELUCRARE',
    'BV': r'BESLOTEN VENNOOTSCHAP|BEPERKTE AANSPRAKELIJKHEID|'
    'BESLOTEN VENNOOTSCHAP MET',
    'KOMB': r'KOMBINATU|KOMBINATY|KOMBINAT',
    'NAT': r'NATIONAAL|NATIONALE|NATIONAL|NATIONAUX',
    'NAZ': r'NAZIONALE|NAZIONALI',
    'CONSOL': r'CONSOLIDATED',
    'CHEM': r'CHEMICKEJ|CHEMICZNY|CHEMICKY|CHEMII|CHEMICALS|CHEMICAL|'
    'CHEMISTRY|CHEMICKE|CHEMISCHE|CHEMISCH|'
    'CHEMICKYCH|CHEMICZNE|CHEMISKEJ|CHEMIE',
    'GHH': r'GUTEHOFFNUNGSCHUTTE|GUTEHOFFNUNGSCHUETTE',
    'ALLG': r'ALLGEMEINE|ALLGEMEINER',
    'STIINT': r'STIINTIFICA',
    'CO': r'COMPANY|COMPANIES',
    'GK': r'GOMEI KAISHA|GOMEI GAISHA|GKGOUSHI GAISHA|GOSHI KAISHA',
    'VVU': r'VYZK VYVOJOVY USTAV|VYZKUMNY VYVOJOVY USTAV',
    'OHG': r'OFFENE HANDELSGESELLSCHAFT',
    'INST NAT': r'INSTITUTE NATIONALE|INSTITUT',
    'CENT': r'CENTRAUX|CENTRAL|CENTRALA|CENTER|CENTRE|CENTRALES|CENTRAAL|CENTRUM|CENTRO|CENTRALE|CENTRUL',
    'DEPT': r'DEPARTEMENT|DEPARTMENT',
    'RES': r'RESEARCH',
    'SAS': r'SOCIETA IN ACCOMANDITA SEMPLICE',
    'SPA': r'SOCIETA PER AZIONI',
    'VVB': r'VEREINIGUNG VOLKSEIGENER BETRIEBUNG',
    'BRDR': r'BRODRENE|BROEDRENE|BRODERNA|BROEDERNA',
    'RIJKSUNIV': r'RIJKSUNIVERSITEIT',
    'SH': r'SHADAN HOUJIN|SHADAN HO',
    'OFF NAT': r'OFFICINE NATIONALE',
    'KB': r'KOMMANDIT BOLAG|KOMMANDITBOLAGET|KOMMANDIT BOLAGET|KOMMANDITBOLAG',
    'ETUD': r'ETUDES|ETUDE',
    'FRAT': r'F LLI|FRATELLI|FLLI',
    'VERW GES': r'VERWALTUNGSGESELLSCHAFT',
    'SOC APPL': r'SOCIETA APPLICAZIONE|SOCIETE APPLICATION',
    'ZENT': r'ZENTRALE|ZENTRALNA|ZENTRALEN|ZENTRALES|ZENTRUM',
    'GH': r'GAKKO HOJIN|GAKKO HOUJIN',
    'BET-GMBH': r'BETEILIGUNGS GESELLSCHAFT MIT|BETEILIGUNGSGESELLSCHAFT MBH|GESELLSCHAFT MIT BESCHRAENKTER',
    'SOC CHIM': r'SOCIETE CHIMIQUE',
    'SNC': r'SOCIETA IN NOME COLLECTIVO|SOCIETE EN NOM COLLECTIF',
    'VEB': r'VOLKSEIGENER BETRIEBE',
    'APS': r'ANPARTSSELSKABET|ANPARTSSELSKAB',
    'APP': r'APPARATUS|APPARECHHI|APPAREIL|APPAREILS|APPARATE|APPARATEBAU|APPAREILLAGES|APPAREILLAGE',
    'PRELUC': r'PRELUCRAREA',
    'GMBH': r'BESCHRANKTER HAFTUNG|GESELLSCHAFT MBH|GESELLSCHAFT MIT',
    'LAB': r'LABORATOIR|LABORATORIOS|LABORATORIJ|LABORATORIES|LABORATOIRES|LABORTORI|LABORATORIO|LABORATORI|LABORATORIEI|LABORATORY|LABORATOIRE|LABORATORIUM|LABORATORII',
    'ONTWIK': r'ONTWIKKELINGS|ONTWIKKELINGSBUREAU',
    'WISS': r'WISSENSCHAFTLICHES|WISSENSCHAFTLICHE',
    'CIE FR': r'COMPAGNIE FRANCAISE',
    'SCHWEIZ': r'SCHWEIZER|SCHWEIZERISCHER|SCHWEIZERISCHES|SCHWEIZERISCH|SCHWEIZERISCHE',
    'SUDDEUT': r'SUDDEUTSCH|SUDDEUTSCHE|SUDDEUTSCHER|SUDDEUTSCHES',
    'KI': r'KUTATO INTEZET|KUTATO INTEZETE|KUTATOINTEZET|KUTATOINTEZETE',
    'OP': r'OBOROVY PODNIK',
    'OFF MEC': r'OFFICINE MECCANICHE|OFFICINE MECCANICA',
    'ZENT INST': r'ZENTRALINSTITUT',
    'DEV': r'DEVELOPMENTS|DEVELOPPEMENTS|DEVELOP|DEVELOPPEMENT|DEVELOPMENT',
    'SOC ALSAC': r'SOCIETE ALSACIENNE',
    'CONSTR': r'CONSTRUCTIONS|CONSTRUCTION|CONSTRUCTII|CONSTRUCTOR|CONSTRUCTIILOR|CONSTRUCCIONE|CONSTRUCCION|CONSTRUCTORTUL|CONSTRUCTIE|CONSTRUCCIONES|CONSTRUCTORUL',
    'HB': r'HANDELS BOLAGET|HANDELSBOLAGET',
    'SOC TECH': r'SOCIETE TECHNIQUE|SOCIETE TECHNIQUES',
    'GES': r'GESELLSCHAFT',
    'SCI': r'SCIENTIFIQUES|SCIENCES|SCIENTIFICA|SCIENCE|SCIENTIFIC|SCIENTIFIQUE',
    'US DEPT': r'UNITED STATES OF AMERICA AS REPRESENTED BY THE UNITED STATES DEPARTMENT',
    'MFG': r'MANUFACTURING|MANUFACTURINGS',
    'SOC EXPL': r'SOCIETE EXPLOITATION',
    'US SEC': r'UNITED STATES OF AMERICA REPRESENTED BY THE SECRETARY|UNITED STATES GOVERNMENT AS REPRESENTED BY THE SECRETARY OF|UNITED STATES OF AMERICA SECRETARY OF',
    'INST FR': r'INSTITUTE FRANCAISE',
    'MFR': r'MANUFACTURER|MANIFATTURA|MANUFACTURAS|MANIFATTURE|MANUFACTURE|MANUFATURA|MANIFATTURAS|MANUFACTURES|MANUFACTURERS',
    'OSTE': r'OSTERREICHISCHE|OSTERREICHISCHES|OSTERREICHISCH',
    'PTY': r'PROPRIETARY',
    'RES & DEV': r'RESEARCH & DEVELOPMENT|RESEARCH AND DEVELOPMENT',
    'LTDA': r'LIMITADA',
    'ZAVOD': r'ZAVODU|ZAVODY',
    'GEN': r'GENERALES|GENERAUX|GENERAL|GENERALE|GENERALA',
    'KUNST': r'KUNSTSTOFFTECHNIK|KUNSTSTOFF',
    'GEBR': r'GEBRUDERS|GEBRODERS|GEBRUEDERS|GEBROEDERS|GEBRUEDER|GEBRUDER|GEB|GEBROEDER|GEBRODER',
    'COOP': r'COOPERATIVA|COOPERATIEVE|CO-OPERATIVE|COOPERATIVES|COOPERATIVE|CO-OPERATIVES',
    'ZH': r'ZAIDAN HOJIN|ZAIDAN HOUJIN',
    'CIE IND': r'COMPAGNIE INDUSTRIALE|COMPAGNIE INDUSTRIELLE|COMPAGNIE INDUSTRIELLES',
    'GRP': r'GROUPMENT|GROUPEMENT',
    'ENG': r'ENGINEERING',
    'WERKZ MASCH KOMB': r'WERKZEUGMASCHINENKOMBINAT',
    'DDR': r'DEMOKRATISCHEN REPUBLIK|DEMOKRATISCHE',
    'KONINK': r'KONINKLIJKE',
    'SOC NOUV': r'SOCIETE NOUVELLE',
    'CIE INT': r'COMPAGNIE INTERNATIONALE',
    'ORG': r'ORGANISATION|ORGANISATIE|ORGANIZZAZIONE|ORGANIZATIONS|OYOSAKEYHTIO|ORGANISATIONS|ORGANIZATION',
    'EV': r'EINGETRAGENER VEREIN',
    'UNIV': r'UNIVERSITAIRE|UNIVERSIDAD|UNIVERSITAT|UNIVERSITA|UNIVERSITA DEGLI STUDI|UNIVERSITETAM|UNIVERSITETY|UNIWERSYTET|UNIVERSITAET|UNIVERSIDADE|UNIVERSITETE|UNIVERSITEIT|UNIVERSITETOV|UNIVERSITAIR|UNIVERSITETOM|UNIVERSITETU|UNIVERSITE|UNIVERSITATEA|UNIVERSITY|UNIVERSITETAMI|UNIVERSITET|UNIVERSITETA',
    'SA': r'SOCIEDAD ANONIMA|SA DITE|SOCIETE ANONYME DITE|SOCIETE ANONYME',
    'PROD CHIM': r'PRODUITS CHIMIQUES|PRODUIT',
    'INSTR': r'INSTRUMENTE|INSTRUMENTS|INSTRUMENTATION|INSTRUMENT',
    'INT': r'INTERNACIONAL|INTERNATIONELLA|INTERNATIONALEN|INTERNAZIONALE|INTERNATIONAL|INTERNATIONAUX|INTERNATIONALE',
    'US': r'UNITED STATES OF AMERICA|UNITED STATES',
    'CIE PARIS': r'COMPAGNIE PARISIENNE|COMPAGNIE PARISIEN|COMPAGNIE PARISIENN',
    'SPRL': r'SOCIETE PRIVEE A RESPONSABILITE LIMITEE',
    'ASSOC': r'ASSOCIATE|ASSOCIACAO|ASSOCIATION|ASSOCIATES|ASSOCIATED',
    'PRODN': r'PRODUKTIONS|PRODUCTIONS|PRODUZIONI|PRODUCTION|PRODUKTION',
    'IND': r'INDUSTRIALIZAREA|INDUSTRIYAM|INDUSTRIYAMI|INDUSTRII|INDUSTRIELLE|INDUSTRIEL|INDUSTRIYAKH|INDUSTRIALS|INDUSTRIYA|INDUSTRY|INDUSTRIALE|INDUSTRIELL|INDUSTRIELS|INDUSTRIE|INDUSTRIALIZARE|INDUSTRIEI|INDUSTRIAS|INDUSTRI|INDUSTRIEELE|INDUSTRIALI|INDUSTRIES|INDUSTRIAL|INDUSTRIJ|INDUSTRIALA|INDUSTRIER|INDUSTRIELLES|INDUSTRIYU|INDUSTRIA',
    'PROD': r'PRODOTTI|PRODUTOS|PRODUCT|PRODUKTE|PRODUITS|PRODUKTER|PRODUKT|PRODUCE|PRODUCTOS|PRODUCTORES|PRODUKCJI|PRODUCTIE|PRODUCTS|PRODUCTA|PRODUSE|PRODUCTAS|PRODUCTO',
    'SIDER': r'SIDERURGIC|SIDERURGICA|SIDERURGIE|SIDERURGICAS|SIDERURGIQUE',
    'WTZ': r'WISSENSCHAFTLICHES TECHNISCHES ZENTRUM',
    'INC': r'INCORPORATED|INCORPORATION',
    'REAL': r'REALISATIONS|REALISATION',
    'FR': r'FRANCAIS|FRANCAISE',
    'ACAD': r'ACADEMY',
    'ESTAB': r'ESTABLISSEMENTS|ESTABLISHMENT|ESTABLISSEMENT|ESTABLISHMENTS',
    'US ADMIN': r'UNITED STATES OF AMERICA ADMINISTRATOR OF',
    'SOC PARIS': r'SOCIETE PARISIENNE|SOCIETE PARISIENN|SOCIETE PARISIEN',
    'FOUND': r'FOUNDATIONS|FOUNDATION',
    'ITAL': r'ITALIANE|ITALI|ITALIANO|ITALIANI|ITALIANA|ITALIEN|ITALIENNE|ITALY|ITALIA|ITALIAN|ITALO',
    'RECH': r'RECHERCHES',
    'IST': r'ISTITUTO',
    'UTIL': r'UTILAJE|UTILISATION|UTILISATIONS|UTILAJ',
    'FA': r'FIRMA',
    'PRZEYM': r'PRZEMYSLU',
    'CHIM': r'CHIMIYU|CHIMIKO|CHIMICO|CHIMIESKOJ|CHIMIYAM|CHIMII|CHIMICA|CHIMIYAKH|CHIMIEI|CHIMIC|CHIMICI|CHIMIYAMI|CHIMIQUES|CHIMIE|CHIMIYA|CHIMICE|CHIMIQUE',
    'UK SEC FOR': r'SECRETARY OF STATE FOR',
    'KGAA': r'KOMMANDIT GESELLSCHAFT AUF AKTIEN|KOMMANDITGESELLSCHAFT AUF AKTIEN',
    'LAVORAZ': r'LAVORAZIONE|LAVORAZA|LAVORAZIO|LAVORAZI|LAVORAZIONI',
    'MASCH': r'MASCHIN|MASCHINENVERTRIEB|MASCHINEN',
    'INSTMSTO': r'INSINO|INSINOEOERITOMISTO',
    'APPL': r'APPLICAZIONI|APPLICATIONS|APPLICATION|APPLICAZIONE',
    'SEC': r'SECRETARY',
    'NORDDEUT': r'NORDDEUTSCHE|NORDDEUTSCH|NORDDEUTSCHER|NORDDEUTSCHES',
    'EXPL': r'EXPLOITATION|EXPLOITATIE|EXPLOATERINGS|EXPLOATERING|EXPLOITATIONS',
    'NP': r'NARODNY PODNIK|NARODNIJ PODNIK|NARODNI PODNIK',
    'TECH': r'TECHNIQUES|TECHNISCHE|TECHNIKAI|TECHNICZNY|TECHNICO|TECHNIK|TECHNISCH|TECHNIQUE|TECHNIKI|TECHNICAL|TECHNISCHES',
    'NV': r'NAAMLOZE VENNOOTSCHAP|NAAMLOOSE VENOOTSCHAP',
    'CIE NAT': r'COMPAGNIE NATIONALE',
    'VER': r'VERENIGING|VEREINIGTE|VEREINIGTES|VEREENIGDE|VEREINIGUNG|VEREIN',
    'CC': r'CLOSE CORPORATION',
    'RECH & DEV': r'RECHERCHES ET DEVELOPMENTS|RECHERCHE|RECHERCHES ET DEVELOPPEMENTS',
    'SRL': r'SOCIEDAD DE RESPONSABILIDAD LIMITADA',
    'MASCHBAU': r'MASCHINENBAUANSTALT|MASCHINENBAU',
    'COSTR': r'COSTRUZIONI',
    'CORP': r'CORPORATE|CORPORATION',
    'PTE LTD': r'PRIVATE LIMITED',
    'LTD': r'LIMITED',
    'COMB': r'COMBINATUL',
    'EURO': r'EUROPEA|EUROPAEISCHES|EUROPE|EUROPEENNE|EUROPAISCHES|EUROPEAN|EUROPAISCHEN|EUROPAEISCHEN|EUROPEEN|EUROPAISCHE|EUROPAEISCHE',
    'OESTERR': r'OESTERREICHISCHES|OESTERREICHISCHE|OESTERREICHISCH|OESTERREICH|OSTERREICH',
    'KG': r'KOMMANDITGESELLSCHAFT|KOMMANDIT GESELLSCHAFT',
    'SARL': r'SOCIETE A RESPONSIBILITE LIMITEE|SOCIETE A RESPONSABILITE LIMITEE',
    'KK': r'KABUSHIKI GAISHA|KABUSHIKI KAISHA|KABUSHIKI KAISYA|KABUSHIKIKAISYA|KABUSHIKIKAISHA',
    'PVBA': r'PERSONENVENNOOTSCHAP MET BEPERKTE AANSPRAKELIJKHEID',
    'SP': r'SDRUZENI PODNIK|SDRUZENI PODNIKU',
    'BET-GES': r'BETEILIGUNGSGESELLSCHAFT',
    'SOC NAT': r'SOCIETE NATIONALE',
    'HANDL': r'HANDELSMAATSCHAPPIJ|HANDELSMIJ',
    'KP': r'KONCERNOVY PODNIK',
    'PLC': r'PUBLIC LIMITED COMPANY',
    'APAR': r'APARATE|APARARII|APARATELOR',
    'ETAB': r'ETABLISSEMENTS|ETABS|ETABLISSEMENT|ETS',
    'SOC CIV': r'SOCIEDAD CIVIL|SOCIETE CIVILE',
    'DEUT': r'DEUTSCH|DEUTSCHLAND|DEUTSCHES|DEUTSCHER|DEUTSCHE|DEUTSCHEN',
    'MASCHFAB': r'MASCHINENFABRIK|MASCHINENFAB|MASCHINENFABRIKEN|MASCHINENFABRIEK',
    'CIA': r'COMPANHIA|COMPAGNIA',
    'SOC ETUD': r'SOCIETE ETUDE|SOCIETE ETUDES',
    'CIE': r'COMPAGNIE',
    'FARM': r'FARMACEVTSKIH|FARMACEUTICHE|FARMACEUTICA|FARMACEUTICI|FARMACEUTICO|FARMACIE|FARMACEUTISK|FARMACEUTICOS|FARMACEUTICE',
    'YG': r'YUUGEN KAISYA|YUGEN GAISHA|YUUGEN KAISHA|YUUGEN GAISHA|YUGEN KAISHA',
    'WESTDEUT': r'WESTDEUTSCHER|WESTDEUTSCHE|WESTDEUTSCH|WESTDEUTSCHES',
    'INST': r'INSTITUUT|INSTITUTT|INSTITUTAMKH|INSTITUTU|INSTYTUT|INSTITUTAM|INSTITUTO|INSTITZHT|INSTITUTA|INSTITUTET|INSTITUTES|INST INSTITUTOM|INSTITUTOV|INSTITUTY|INSTITUTUL|INSTITUTAMI|INSTITUTE',
    'AGRI': r'AGRICULTURAL|AGRICOLE|AGRICOLAS|AGRICOLTURE|AGRICOLES|AGRICULTURE|AGRICOLI|AGRICOLA|AGRICULTURA',
    'FOND': r'FONDAZIONE|FONDATION',
    'SOC GEN': r'SOCIETE GENERALE',
    'DIV': r'DIVISIONE|DIVISION',
    'SPITAL': r'SPITALUL',
    'SOC COMML': r'SOCIETE COMMERCIALES|SOCIETE COMMERCIALE',
    'SOC': r'SOCIETA|SOCIETY|SOCIEDADE|SOCIEDAD|SOCIETE',
    'MBH': r'MIT BESCHRANKTER HAFTUNG',
    'PRZEDSIEB': r'PRZEDSIEBIOSTWO',
    'SOC IND': r'SOCIETE INDUSTRIELLE|SOCIETE INDUSTRIELLES',
    'LP': r'LIMITED PARTNERSHIP',
    'FAB': r'FABBRICA|FABRIZIO|FABRIKER|FABBRICHE|FABRIK|FABRICA|FABRIQUE|FABRICATIONS|FABRIEKEN|FABRICATION|FABRIEK|FABRYKA|FABBRICAZIONI|FABRIQUES',
    'COMML': r'COMMERCIAL|COMMERCIALE',
    'AB': r'AKTIEBOLAGET|AKTIEBOLAG',
    'UK': r'UNITED KINGDOM',
    'VERW': r'VERWALTUNGS|VERWALTUNGEN|VERWERTUNGS',
    'AKAD': r'AKADEMIYU|AKADEMIYAM|AKADEMIYAMI|AKADEMIYA|AKADEMIA|AKADEMI|AKADEMIJA|AKADEMIYAKH|AKADEMII|AKADEMIE|AKADEMIEI',
    'ANTR': r'ANTREPRIZA',
    'SOC AUX': r'SOCIETE AUXILIAIRE',
    'AS': r'AKTIESELSKABET|A/S|AKTIESELSKAB',
    'BROS': r'BROTHERS',
    'VU': r'VYZKUMNY USTAV|VYZK USTAV|VYZKUMNYUSTAV',
    'INTR': r'INTREPRINDEREA',
    'CIE GEN': r'COMPAGNIE GENERALE',
    'GEW': r'GEWERKSCHAFT',
    'MTA': r'MAGYAR TUDOMANYOS AKADEMIA',
    'SOC ESPAN': r'SOCIEDAD ESPANOLA',
    'WERKZ MASCHFAB': r'WERKZEUGMASCHINENFABRIK',
    'SOC MEC': r'SOCIETE MECANIQUES|SOCIETE MECANIQUE',
    'ING': r'INGENIEURBUERO|INGENIEUR|INGENIORSFIRMA|INGENIERIA|INGENIORSFIRMAN|'
    'INGENIEURBURO|INGENIEURTECHNISCHES|INGENIEURBUREAU|INGENIEURS|INGENIEURSBUREAU|'
    'INGENIOERFIRMAET|INGENJORSFIRMA|INGENIEURGESELLSCHAFT|INGINERIE|'
    'INGENIEURTECHNISCHE|INGENIER',
    'CERC': r'CERCETARI|CERCETARE',
    'VEB KOMB': r'VEB KOMBINAT',
    'TELECOM': r'TELECOMMUNICAZIONI|TELECOMMUNICATION|TELECOMUNICAZIONI|'
    'TELECOMMUNICATIONS|TELECOMMUNICACION',
    'PROI': r'PROIECTARE|PROIECTARI',
    'PHARM': r'PHARMACEUTIQUES|PHARMAZIE|PHARMACEUTICA|PHARMAZEUTISCHE|'
    'PHARMAZEUTISCHEN|PHARMACEUTICALS|PHARMAZEUTISCH|PHARMACEUTIQUE|'
    'PHARMACEUTICAL|PHARMAZEUTIKA',
    'ZENT LAB': r'ZENTRALLABORATORIUM',
    'EQUIP': r'EQUIPMENT|EQUIPEMENT|EQUIPEMENTS|EQUIPMENTS',
    'TRUST': r'TRUSTUL',
    'AKTIENGESELLSCHAFT': r'AGACTIEN GESELLSCHAFT|ACTIENGESELLSCHAFT|'
    'AKTIEN GESELLSCHAFT'
    }
