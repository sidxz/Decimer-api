from app.core.logging_config import logger
from app.utils.daikon_api import get_molecule_by_smiles

def search_daikon(document, results):
    """
    Example hook for processing data in Pipeline 1.
    """
    try:
        logger.info("[START HOOK] Daikon Molecule DB search")
        for result in results:
            logger.info(f"RESULT = {result}")
            result.print_result()
            # Implement the Daikon API call here
            daikon_response = get_molecule_by_smiles(result.predicted_smiles)
            if daikon_response:
                result.daikon_molecule_id = daikon_response[0]["id"]
                result.daikon_molecule_name = daikon_response[0]["name"]
                document.daikon_molecule_ids.append(result.daikon_molecule_id)
                document.molecule_tags.append(result.daikon_molecule_name)
                result.add_history(
                    "Daikon Search",
                    "Success",
                    f"Found molecule {result.daikon_molecule_name} with ID: {result.daikon_molecule_id}",
                )
                logger.info(
                    f"Found molecule {result.daikon_molecule_name} with ID: {result.daikon_molecule_id}"
                )
            else:
                result.add_history(
                    "Daikon Search", "Failure", "Molecule not found in Daikon DB"
                )
    except Exception as e:
        logger.error(f"An error occurred during Daikon search: {str(e)}")
        return None
    finally:
        logger.info("[END HOOK] Daikon Molecule DB search end.")
        

hooks = [search_daikon]
