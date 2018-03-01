pragma solidity ^0.4.18;

library SafeMath {
    function add(uint a, uint b) internal pure returns (uint c) {
        c = a + b;
        require(c >= a);
    }
    function sub(uint a, uint b) internal pure returns (uint c) {
        require(b <= a);
        c = a - b;
    }
    function mul(uint a, uint b) internal pure returns (uint c) {
        c = a * b;
        require(a == 0 || c / a == b);
    }
    function div(uint a, uint b) internal pure returns (uint c) {
        require(b > 0);
        c = a / b;
    }
}
contract ERC20Interface {
    function totalSupply() public constant returns (uint);
    function balanceOf(address tokenOwner) public constant returns (uint balance);
    function allowance(address tokenOwner, address spender) public constant returns (uint remaining);
    function transfer(address to, uint tokens) public returns (bool success);
    function approve(address spender, uint tokens) public returns (bool success);   //Can we revert() and be valid? Need variables as arguments
    function transferFrom(address from, address to, uint tokens) public returns (bool success);

    event Transfer(address indexed from, address indexed to, uint tokens);      
    event Approval(address indexed tokenOwner, address indexed spender, uint tokens); 
    event Buy(address indexed buyer, uint tokens);
    event LoanPayment(address indexed from, address indexed LoanWallet, uint tokens);
}

contract ApproveAndCallFallBack {
    function receiveApproval(address from, uint256 tokens, address token, bytes data) public;
}

contract Owned {
    address public owner;
    address public newOwner;
    address CTO_addr= 0x0; 
    address CPO_addr= 0x0; 
    event OwnershipTransferred(address indexed _from, address indexed _to);

    function Owned() public {
        owner = msg.sender;
    }
    modifier only_CPO {
        require( (msg.sender == CPO_addr) || (msg.sender == owner) );
        _;        
    }   
    modifier only_CTO {
        require( (msg.sender == CTO_addr) || (msg.sender == owner) );
        _;        
    }
    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
    function transferCTO(address _newCTO) public onlyOwner {
        CTO_addr = _newCTO;
    }
    function transferCPO(address _newCPO) public onlyOwner {
        CPO_addr = _newCPO;
    } 
    function transferOwnership(address _newOwner) public onlyOwner {
        newOwner = _newOwner;
    }
    function acceptOwnership() public {
        require(msg.sender == newOwner);
        OwnershipTransferred(owner, newOwner);
        owner = newOwner;
        newOwner = address(0);
    }
}

contract TheLendingCoin is ERC20Interface, Owned {
    using SafeMath for uint;
    string public symbol;
    string public  name;
    uint8 public decimals;
    uint256 public _totalSupply;
    uint256 public _currentSupply;
    
    uint256 public EthertoQMCT;            //store 1e9 in variable, precision on decimal is billions
    uint16 public blocksPriceWindow;    //8 is 2 minutes for market manipulation
    uint256 public end_block;
    uint256 public start_block;

    mapping(address => uint) public balances;
    mapping(address => mapping(address => uint)) allowed;   //Hate But Keep

    function MediaCoin() public {
        symbol = "QMCT";
        name = "MediaCoin";
        decimals = 18;
        _totalSupply = 1e9 * 10**uint(decimals);   //includes https://etherscan.io/address/0x0000000000000000000000000000000000000000
        EthertoQMCT =1e3;    //in pennies, actually a decimal ratio, updating 6 decimal by multiply conversion
        end_block = 0; //ICO is off and disabled
        start_block=0;
        _currentSupply = 0;
    }
    
    function updateEtoQMCT (uint256 QMCTpriceInEther) only_CPO public {
        EthertoQMCT=QMCTpriceInEther;
    }
    function updateblocksPriceWindow (uint16 _moreblocks) only_CTO public {
        blocksPriceWindow = _moreblocks;
    }
    
    function loanPayTLC (address to, uint tokens) public returns (bool success) {
        if(LoanBalanceUSDc[to] > 0){
            balances[msg.sender] = balances[msg.sender].sub(tokens);
            balances[to] = balances[to].add(tokens);    //wallet of loan
            minusByTLC(to, tokens); //by payee to a loan
            LoanPayment(msg.sender, to, tokens);    //announce event
        } else {
            revert();
            return false; //implied, won't run
        }
        return true;
    }
    function minusByTLC (address loan_addr, uint256 paidTLC) internal  { //payment comes from blockchain
        if(block.number <= LastPriceUpdateBlock + blocksPriceWindow ) {
        uint256 paidTLCinUSDc = paidTLC.mul(TLCtoUSDc).div(1e6).div(10**uint(decimals)); //restore the ratio back to decimals, wei to pennies
        LoanBalanceUSDc[loan_addr] = LoanBalanceUSDc[loan_addr].sub(paidTLCinUSDc);
        } else { 
            revert();
        }
    }
    function totalSupply() public constant returns (uint) {
        return _totalSupply;
    }
    function currentSupply() public constant returns (uint) {
        return _currentSupply;
    }
    function balanceOf(address tokenOwner) public constant returns (uint balance) {
        return balances[tokenOwner];
    }
    function loanBalanceOf(address tokenOwner) public constant returns (uint loanbalance) {
        return LoanBalanceUSDc[tokenOwner];
    }    
    function transfer(address to, uint tokens) public returns (bool success) {
        balances[msg.sender] = balances[msg.sender].sub(tokens);
        balances[to] = balances[to].add(tokens);
        Transfer(msg.sender, to, tokens);
        return true;
    }
    function approve(address spender, uint tokens) public returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        Approval(msg.sender, spender, tokens);
        return true;
    } 
    function transferFrom(address from, address to, uint tokens) public returns (bool success) {
        balances[from] = balances[from].sub(tokens);
        allowed[from][msg.sender] = allowed[from][msg.sender].sub(tokens);
        balances[to] = balances[to].add(tokens);
        Transfer(from, to, tokens);
        return true;
    }
    function allowance(address tokenOwner, address spender) public constant returns (uint remaining) {
        return allowed[tokenOwner][spender];
    }  
    function approveAndCall(address spender, uint tokens, bytes data) public returns (bool success) {
        allowed[msg.sender][spender] = tokens;
        Approval(msg.sender, spender, tokens);
        ApproveAndCallFallBack(spender).receiveApproval(msg.sender, tokens, this, data);
        return true;
    }  
    function() payable public  {
        if(block.number < end_block && block.number > start_block ) { //Is direct token sale running?
            uint token_amt = msg.value.mul(1e3); //number of tokens in wei, millions precision on ETHtoTLC
            if( _currentSupply.add(token_amt) > _totalSupply) { 
                revert();
            }        
            _currentSupply = _currentSupply.add(token_amt);
            balances[msg.sender] = balances[msg.sender].add(token_amt);
            Buy(msg.sender, token_amt);
        } else {    //If not ICO time period, refund ETH
            revert();
        }
    }
    
    function extendICO(uint256 _blocks) onlyOwner public {
        end_block = block.number + _blocks;
        start_block= block.number;
    }
    function closeICO() onlyOwner public {
        withdraw();         //added withdraw on close
        end_block=block.number;
    }
    function withdraw() onlyOwner public {
        owner.transfer(this.balance);
    }
    function tokenGrant(address receiver, uint token_amt) onlyOwner public {            
        if( _currentSupply.add(token_amt) > _totalSupply) { 
            revert();
        }
        balances[receiver] = balances[receiver].add(token_amt);
        _currentSupply =_currentSupply.add(token_amt);
        Buy(receiver, token_amt);
    } 
    function transferAnyERC20Token(address tokenAddress, uint tokens) public onlyOwner returns (bool success) 
    {
        return ERC20Interface(tokenAddress).transfer(owner, tokens);
    } //Send owner any ERC20 tokens received
}
