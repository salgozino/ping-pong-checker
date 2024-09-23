import sys
import logging

from contract import Contract


def setup_logger(log_file="logs.log", level=logging.INFO):
    # Configure log file
    name = "pong-checker"
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger.setLevel(level)
    fileHandler = logging.FileHandler(f"logs/{log_file}", mode="a")
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    return logger


def main(candidate_bot: str, candidate_starting_block: int, logger: logging.Logger):
    logger.info(
        f"Starting to review pongs for candidate: {candidate_bot} since block: {candidate_starting_block}"
    )
    contract_address = "0xA7F42ff7433cB268dD7D59be62b00c30dEd28d3D"
    ping_pong_contract = Contract(contract_address, "PingPongABI.json", logger)

    all_pings = ping_pong_contract.get_all_pings(candidate_starting_block)
    # logger.info(f"Ping example: {all_pings[0]}")
    all_pongs = ping_pong_contract.get_all_pongs(
        candidate_starting_block, candidate_bot
    )
    # logger.info(f"Pong example: {all_pongs[0]}")
    logger.info(f"Pings: {len(all_pings)} | Pongs: {len(all_pongs)}")

    # Let's check the ping arg in pong events agains the ping txs.
    pings_hash_in_pongs = set([pong["args"]["txHash"] for pong in all_pongs])
    ping_txs = [ping["transactionHash"] for ping in all_pings]

    # Same amount of pongs than pings?
    if len(all_pongs) != len(all_pings):
        logger.error(
            "There is no 1 pong event per ping. Don't know yet if there are duplicates or missing."
        )

    # Duplicated pongs check.
    if len(all_pongs) != len(pings_hash_in_pongs):
        logger.error("There are duplicated pingHash in pongs")
    else:
        logger.info("There are not duplicated pingHash in pongs")

    # Check if all the pong tx args match with the ping txs.
    for pong_hash in pings_hash_in_pongs:
        if not pong_hash in ping_txs:
            logger.error(f"Pong {pong_hash} not included in the pings txs")
    logger.info("All pongs events has a valid ping tx")

    # Missing pings
    if len(pings_hash_in_pongs) < len(all_pings):
        logger.error(
            f"There are {len(pings_hash_in_pongs) / len(all_pings) * 100:.2f}% missing ping txs"
        )
        missing_pings = [
            ping.transactionHash
            for ping in all_pings
            if not ping in pings_hash_in_pongs
        ]
        logger.error(f"Missing pings: {missing_pings}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 main.py <candidate_bot> <candidate_starting_block>")
        sys.exit(1)

    candidate_bot = sys.argv[1]
    candidate_starting_block = int(sys.argv[2])
    logger = setup_logger(candidate_bot)
    main(candidate_bot, candidate_starting_block, logger)
