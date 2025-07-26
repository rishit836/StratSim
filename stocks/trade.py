from decimal import Decimal
from .models import Portfolio, holding, Transaction
import yfinance as yf
from mainapp.models import growth


def execute_trade(request, user,ticker,action,quantity):
    quantity = int(quantity)
    ticker_data = yf.Ticker(ticker)

    print(user.username, "wants to",action.lower(),quantity,"shares of",ticker,".")
    try:
        # getting current price for the stock
        current_price = Decimal(str(ticker_data.info['regularMarketPrice']))
    except:
        return False,"unable to fetch price right now,try later"
    

    # getting total cost of the stocks user wants to buy/sell
    total_cost = current_price * Decimal(quantity)
    # getting the portfolio object for the user incase forgot to make migrations (not possible tho but better safe)
    try:
        # portfolio object to be updated later
        portfolio = Portfolio.objects.get(user=user)
    except:
        return False, "portfolio doesnt exist for " + str(user.username)
    
    # for debugging 
    print("Before Trade: ",round(portfolio.current_funds,2), "|",round(portfolio.invested_amount,2))
    if action.lower() == "buy":
        if portfolio.current_funds < total_cost:
            print("insufficient funds.")
            return False, "insufficient funds you need $ " +str(abs(portfolio.current_funds - total_cost)) + " more."
        
        # creates a holding incase user doesnt own any stock of the particular ticker
        stock,created = holding.objects.get_or_create(user=user,ticker=ticker,
                                                    #   default parameters to create a object in case holding doesnt already exist
                                                      defaults={'quantity': quantity,'avg_buy_price': current_price,'current_price': current_price,}
        )
        # if user already owns the stock and it wasnt created
        if not created:
            # new quantity of stocks owned
            print("before",stock.quantity)
            total_quantity = stock.quantity + quantity

            # update the avg buy price for the user (incase user buys at a higher price/ or lower price)
            stock.avg_buy_price = ( (stock.avg_buy_price * stock.quantity + current_price * quantity) / total_quantity)
            # update the quantity
            stock.quantity = total_quantity
            # update the current price of the stock
            stock.current_price = current_price
            # save the holding of the stock in the user holding
            stock.save()

        portfolio.invested_amount += total_cost
    elif action.lower() == "sell":
        # check if the user owns a holding of the stock or not
        try:
            stock = holding.objects.get(user=user, ticker=ticker)
            
        except holding.DoesNotExist:
            print("No holding exist please buy first")
            return False,"you dont have any shares of the stock: "+ str(ticker)
        
        if stock.quantity < quantity:
            print("user doesnt own enough shares to sell")
            return False,"not enough shares to sell"
        
        # present price of the stocks
        proceeds = current_price * quantity
        # how much money was invested by user
        cost_basis = stock.avg_buy_price * quantity
        # profit/loss made by user
        realized_pnl = proceeds - cost_basis

        # update the portfolio for the user to show the loss/profit made
        portfolio.initial_funds = portfolio.current_funds
        portfolio.current_funds += realized_pnl
        portfolio.invested_amount -= cost_basis

        # update the quantity of the share in case user is only selling few shares and keeping the rest
        stock.quantity -= quantity
        stock.current_price = current_price

        # deleting the holding incase user is selling all the shares
        if stock.quantity == 0:
            stock.delete()
        else:
            print(stock)
            stock.save()
    else:
        print("INVALID ACTION")
        return False,"Invalid Action"
    
    # logging the transaction for the user
    Transaction.objects.create(
        user=user,
        ticker=ticker,
        action=action.upper(),
        quantity=quantity,
        price=current_price
    )

    # Save updated portfolio
    portfolio.update_return_history()
    portfolio.save()

    user_growth, _ = growth.objects.get_or_create(user=user)
    user_growth.push(float(portfolio.current_funds)) 

    return True,"your trade was succesfull check the dashboard for the changes!"

        


