var Account = (function() {
    function Account(x) {
        this.x = x;

        this.myFunc = function() {
            console.log('x is ', x);
        }
    }

    return Account;
})();

var account = new Account(1);
account.myFunc();

