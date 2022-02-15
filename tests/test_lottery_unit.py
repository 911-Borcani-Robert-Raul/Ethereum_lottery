# 0.0125
# 12500000000000000

from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONEMENTS, get_account, fund_with_link, get_contract
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()
    # Arrange
    deploy_lottery()
    lottery = Lottery[-1]
    # Act
    entrance_fee = lottery.getEntranceFee()
    # Assert
    
    # 3000 ETH / USD
    # 50 USD entrance fee
    # We need 50 / 30000 ETH = 0.0166
    expected_entrance_fee = Web3.toWei(50 / 3000, 'ether')

    assert entrance_fee == expected_entrance_fee

def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()
    deploy_lottery()
    lottery = Lottery[-1]

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()
    deploy_lottery()
    lottery = Lottery[-1]
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account

def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()
    deploy_lottery()
    lottery = Lottery[-1]
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)

    # Act
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONEMENTS:
        pytest.skip()
    deploy_lottery()
    lottery = Lottery[-1]
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    fund_with_link(lottery)

    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]

    starting_balance = account.balance()
    lottery_balance = lottery.balance()

    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(request_id, STATIC_RNG, lottery.address, {"from": account})

    # 777 % 3 == 0 => account is winner
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance + lottery_balance
     

    
