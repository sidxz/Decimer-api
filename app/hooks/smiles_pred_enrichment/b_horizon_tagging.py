from app.core.logging_config import logger
from app.utils.daikon_api import (
    get_horizon_associations,
    get_horizon_target,
    get_molecule_by_smiles,
)


def b_horizon_tagging(document, results):
    """
    Example hook for processing data in Pipeline 1.
    """
    try:
        logger.info("[START HOOK] Daikon Horizon search")
        for molId in document.daikon_molecule_ids:
            logger.info(f"Molecule ID = {molId}")
            # Implement the Daikon API call here
            mol_res = get_horizon_associations(molId)
            if mol_res:
                for r in mol_res:
                    rel_id = r.get("id")
                    nm = r.get("nodeName")
                    document.tags.append(nm)
                    logger.info(f"Horizon node result = {nm}")

                    # Also tag the target
                    target_res = get_horizon_target(rel_id)
                    if target_res:
                        target_nm = target_res.get("name")
                        document.tags.append(target_nm)
                        logger.info(f"Horizon target result = {target_nm}")

    except Exception as e:
        logger.error(f"An error occurred during Daikon search: {str(e)}")
        return None
    finally:
        logger.info("[END HOOK] Daikon Molecule DB search end.")


hooks = [b_horizon_tagging]
