def disable_contracts():
    try:
        import contracts
        contracts.disable_all()
    except ImportError:
        pass

def defuse_xml():
    try:
        from safe_lxml import defuse_xml_libs
        defuse_xml_libs()
    except ImportError:
        pass
