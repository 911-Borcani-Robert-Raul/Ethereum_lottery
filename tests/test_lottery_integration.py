from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONEMENTS, fund_with_link


from brownie import network, Lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONEMENTS, get_account
import pytest
from scripts.deploy_lottery import deploy_lottery
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()

    deploy_lottery()
    lottery = Lottery[-1]
    account = get_account()

    print(account)

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000})

    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})

    time.sleep(360)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
