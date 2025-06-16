from decimal import Decimal
from .models import Portfolio, holding, Transaction
import yfinance as yf

def execute_trade(request, user, ticker, action, quantity):
    quantity = int(quantity)
    ticker_data = yf.Ticker(ticker)

    try:
        current_price = Decimal(str(ticker_data.info['regularMarketPrice']))
    except Exception as e:
        print(f"❌ Failed to fetch price for {ticker}: {e}")
        return False

    total_cost = current_price * Decimal(quantity)

    try:
        portfolio = Portfolio.objects.get(user=user)
    except Portfolio.DoesNotExist:
        print("❌ No portfolio found")
        return False

    print(f"Before Trade: 💰 {portfolio.current_funds:.2f} | 📈 {portfolio.invested_amount:.2f}")

    if action.upper() == "BUY":
        if portfolio.current_funds < total_cost:
            print("❌ Not enough funds to buy")
            return False

        stock, created = holding.objects.get_or_create(
            user=user,
            ticker=ticker,
            defaults={
                'quantity': quantity,
                'avg_buy_price': current_price,
                'current_price': current_price,
            }
        )

        if not created:
            total_quantity = stock.quantity + quantity
            stock.avg_buy_price = (
                (stock.avg_buy_price * stock.quantity + current_price * quantity) / total_quantity
            )
            stock.quantity = total_quantity
            stock.current_price = current_price
            stock.save()

        # Update portfolio
        portfolio.current_funds -= total_cost
        portfolio.invested_amount += total_cost

    elif action.upper() == "SELL":
        try:
            stock = holding.objects.get(user=user, ticker=ticker)
        except holding.DoesNotExist:
            print("❌ No holdings to sell")
            return False

        if stock.quantity < quantity:
            print("❌ Not enough shares to sell")
            return False

        proceeds = current_price * quantity
        cost_basis = stock.avg_buy_price * quantity
        realized_pnl = proceeds - cost_basis

        portfolio.current_funds += proceeds
        portfolio.invested_amount -= cost_basis

        stock.quantity -= quantity
        stock.current_price = current_price
        if stock.quantity == 0:
            stock.delete()
        else:
            stock.save()

        print(f"💸 Realized PnL: ₹{realized_pnl:.2f}")

    else:
        print("❌ Invalid action")
        return False

    # Log the transaction
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

    print(f"✅ Trade executed: {action.lower()} {quantity} of {ticker} @ ₹{current_price}")
    print(f"💰 Current Funds: ₹{portfolio.current_funds:.2f}")
    print(f"📈 Invested Amount: ₹{portfolio.invested_amount:.2f}")
    print(f"📊 Return: {portfolio.previous_return_percent:.2f}%")

    return True
