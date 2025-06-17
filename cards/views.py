from decimal import Decimal
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import User, Card, Transaction, UserCard, TransactionCategory, UserCategory
from django.http import HttpResponse
from .generate_pdf import generate_qr_pdf

from django.db.models import Sum
from django.db.models.functions import TruncDate

## BAR Section

@login_required(login_url='login')
def bar_home(request):
    messages = []
    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        card_code = request.POST.get('card_code')

        try:
            c = None
            if not card_number:
                c = Card.objects.filter(card_number=card_code).first()
            elif not card_code:
                c = Card.objects.filter(id=card_number).first()

            card = UserCard.objects.filter(card=c).first()

            if not card:
                messages.append({
                    'tag': 'error',
                    'text': 'Carta non trovata. Riprova con un altro numero di carta o codice.'
                })

            elif card.status != 'active':
                messages.append({
                    'tag': 'error',
                    'text': f'Carta non attiva. Stato: {card.status}. Motivo: {card.notes if card.notes else "Nessun motivo fornito."}'
                })
            else:
                return redirect('bar_transaction', id=card.user.id)
            
        except Exception as e:
            messages.append({
                'tag': 'error',
                'text': f'Errore: {str(e)}'
            })
        
    return render(request, 'cards/bar_home.html', {
        "messages": messages,
    })

@login_required(login_url='login')
def bar_transaction(request, id):
    user = User.objects.filter(id=id).first()
    if not user:
        return render(request, 'cards/bar_transaction.html', {'messages': [{'tag': 'error', 'text': 'Utente non trovato.'}]})
    
    messages = []
    transaction_success = False
    
    # create a new transaction for the user with amount, notes, category in post request and save in card_id his current active card
    if request.method == 'POST':
        amount = - abs(float(request.POST.get('amount', 0)))

        # notes = request.POST.get('notes')
        # category = request.POST.get('category')
        # card = UserCard.objects.filter(user=user, status='active').first()

        created_by = request.user
        card = UserCard.objects.filter(user=id, status='active').first()

        # calculate user balance
        transactions = Transaction.objects.filter(user_id=user)
        balance = sum(t.amount for t in transactions)
        if Decimal(balance) + Decimal(amount) < Decimal(0):
            print(f"logg Balance: {balance}, Amount: {amount}")
            import logging
            logger = logging.getLogger(__name__)

            logger.error(f"Saldo insufficiente per l'utente {user.name} {user.surname}. Saldo attuale: {Decimal(balance)}, Importo della transazione: {Decimal(amount)}. operazione risultato: {Decimal(balance) + Decimal(amount)}")

            messages.append({
                'tag': 'error',
                'text': 'Saldo insufficiente per questa transazione.'
            })
            return render(request, 'cards/bar_transaction.html', {
                "user": user,
                "balance": balance,
                "messages": messages,
                "trs": transaction_success
            })

        if card:
            transaction = Transaction(
                card_id=card.card,
                user_id=user,
                amount=amount,
                # notes=notes,
                category=TransactionCategory.objects.order_by('name').first(),
                created_by=created_by
            )
            transaction.save()
            messages.append({
                'tag': 'success',
                'text': 'Transazione creata con successo.'
            })
            transaction_success = True
            # return redirect('bar_transaction', id=user_id, messages=[{
            #     'tag': 'success',
            #     'text': 'Transazione creata con successo.'
            # }])
        else:
            messages.append({
                'tag': 'error',
                'text': 'Nessuna carta attiva trovata per questo utente.'
            })
    
    transactions = Transaction.objects.filter(user_id=user)
    balance = sum(t.amount for t in transactions)
    transaction_category = TransactionCategory.objects.all()

    user_id = user.id
    card_id = UserCard.objects.filter(id=user.id, status='active').first()
 
    context = {
        "user": user,
        "user_id": user_id,
        "card_id": card_id,
        "balance": balance,
        "messages": messages,
        "trs": transaction_success
    }
    return render(request, 'cards/bar_transaction.html', context)

## END BAR

## CARDS Management Section

@login_required(login_url='login')
def cards(request):
    q = request.GET.get('q')
    if q:
        users = User.objects.filter(name__icontains=q) | User.objects.filter(surname__icontains=q)
    else:
        users = User.objects.all()[:10]
    tr = Transaction.objects.filter(user_id__in=users)
    for user in users:
        user.transactions = tr.filter(user_id=user)
        user.balance = sum(transaction.amount for transaction in user.transactions)

    context = {
        "users": users
    }
    return render(request, 'cards/cards.html', context)

@login_required(login_url='login')
def cards_single(request, id):

    user = User.objects.filter(id=id).first()
    if not user:
        return render(request, 'cards/cards_single.html', {"error": "User not found"})
    
    message = request.GET.get('message')
    message_type = request.GET.get('message_type')
    
    # create a new transaction for the user with amount, notes, category in post request and save in card_id his current active card
    if request.method == 'POST':
        amount = request.POST.get('amount')
        notes = request.POST.get('notes')
        category = request.POST.get('category')
        card = UserCard.objects.filter(user=user, status='active').first()
        created_by = request.user
        
        if card:
            transaction = Transaction(
                card_id=card.card,
                user_id=user,
                amount=amount,
                notes=notes,
                category=TransactionCategory.objects.filter(id=category).first(),
                created_by=created_by
            )
            transaction.save()
            message = 'Ricarica effettuate con successo'
            message_type = 'success'
            
            # return redirect('cards_single', id=user.id)
            return redirect(reverse('full_screen_message') + f'?message={message}&message_type={message_type}&redirect_url={reverse("cards_single", args=[user.id])}')
        else:
            message = 'No active card found for this user.'
            message_type = 'error'
    
    
    tr = Transaction.objects.filter(user_id=user)
    cc = UserCard.objects.filter(user=user)
    tc = TransactionCategory.objects.all()

    user.transactions = tr.filter(user_id=user)
    user.total_spent = sum(transaction.amount for transaction in user.transactions)
    user.positive_balance = sum(transaction.amount for transaction in user.transactions if transaction.amount > 0)
    user.negative_balance = sum(transaction.amount for transaction in user.transactions if transaction.amount < 0)
        
    
    context = {
        "user": user,
        "tr": tr,
        "cc": cc,
        "tc": tc,
        "message": request.message if 'message' in request else '',
        "message_type": request.message_type if 'message_type' in request else '',
    }
    return render(request, 'cards/cards_single.html', context)
    
@login_required(login_url='login')
def cards_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        category = request.POST.get('category')
        
        user = User(name=name, surname=surname,category=UserCategory.objects.filter(id=category).first())
        user.save()
    
        return redirect('cards_single', id=user.id)
    
    context = {
        "categories": UserCategory.objects.all().order_by('name'),
    }

    return render(request, 'cards/cards_create.html', context=context)
  
@login_required(login_url='login')
def cards_gen(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        card_id = request.POST.get('card_number')
        notes = request.POST.get('suspnotes', '')

        c = Card.objects.filter(card_number=card_id).first()
        if UserCard.objects.filter(card = c).first() is not None:
            message = 'La carta è già stata assegnata a un utente.'
            message_type = 'error'
            return redirect(reverse('full_screen_message') + f'?message={message}&message_type={message_type}&redirect_url={reverse("cards_single", args=[user_id])}')

        UserCard.objects.filter(user_id=user_id, status='active').update(status='suspended', created_by=request.user, notes=notes)

        u = User.objects.filter(id=user_id).first()
        c = Card.objects.filter(card_number=card_id).first()
        
        x = UserCard(user=u, card=c, status='active', created_by=request.user)
        x.save()

        return redirect('cards_single', id=user_id)


@login_required(login_url='login')
def cards_print(request):
   return render(request, 'cards/cards_print.html')

@login_required(login_url='login')
def cards_print_gen(request):
    
    if request.method == 'POST':
        number_of_cards = int(request.POST.get('num_cards', 1))

        cards = []

        for _ in range(number_of_cards):
            c = Card()
            c.save()
            cards.append(c)
        
        code_list = [(str(card.card_number), str(card.id)) for card in cards]

        out = generate_qr_pdf(code_list)
        output_pdf = out.output(dest='S') #pdf.output(dest='S')
    

        response = HttpResponse(bytes(output_pdf, encoding='latin-1'), content_type='application/pdf')
        response['Content-Disposition'] = "attachment; filename=tessere.pdf"
        return response


@login_required(login_url='login')
def search_card(request):
    if request.method == 'POST':
        card_number = request.POST.get('card_code')
        if card_number:
            card = Card.objects.filter(card_number=card_number).first()
            if card:
                user_card = UserCard.objects.filter(card_id=card).first()
                if user_card:
                    return redirect('cards_single', id=user_card.user.id)
                else:
                    return redirect('cards')
            else:
                return redirect('cards')
        else:
            return redirect('cards')

## END CARDS Management Section

def full_screen_message(request):
    message = request.GET.get('message', 'No message provided.')
    message_type = request.GET.get('message_type', 'info')
    redirect_url = request.GET.get('redirect_url', 'cards')

    return render(request, 'cards/full_screen_message.html', {
        'message': message,
        'message_type': message_type,
        'redirect_url': redirect_url
    })


## CARD INFO Section

def card_info(request):

    card_number = request.GET.get('cardNumber')
    try:
        if card_number:
            card = Card.objects.filter(card_number=card_number).first()
            if card:
                user_card = UserCard.objects.filter(card_id=card).first()

                if user_card:

                    # if user_card.status != 'active':
                    #     return render(request, 'cards/card_info.html', {
                    #         "messages": [{
                    #             'tag': 'error',
                    #             'text': f'Card is not active. Status: {user_card.status}. Reason: {user_card.notes if user_card.notes else "No reason provided."}'
                    #         }]
                    #     })

                    user = user_card.user
                    transactions = Transaction.objects.filter(user_id=user)

                    # Calculate total spent, positive and negative balance
                    total_spent = sum(transaction.amount for transaction in transactions)
                    return render(request, 'cards/card_info.html', {
                        'card': card,
                        'user': user,
                        'user_card': user_card,
                        'transactions': transactions,
                        'total_spent': total_spent,
                    })
                else:
                    return render(request, 'cards/card_info.html', {"messages": [{
                        'tag': 'error',
                        'text': 'Non sono state trovte tessere attive per questo utente.'
                    }]})
            else:
                return render(request, 'cards/card_info.html', {"messages": [{
                    'tag': 'warning',
                    'text': 'La tessera non è stata trovata.'
                }]})
        else:
            return render(request, 'cards/card_info.html', {"messages": [{
                'tag': 'info',
                'text': 'Scansiona la tessera con il lettore per visualizzare il credito residuo.'
            }]})
    except Exception as e:
        return render(request, 'cards/card_info.html', {"messages": [{
            'tag': 'error',
            'text': f'An error occurred: {str(e)}'
        }]})
    

@login_required(login_url='login')
def transaction_summary_view(request):
    # Group by date and category, and calculate the total amount
    transactions = (
        Transaction.objects
        .values('category__name', date=TruncDate('created_at'))
        .annotate(total_amount=Sum('amount'))
        .order_by('date', 'category__name')
    )

    # Structure the data into a nested dict: {date: {category: total, ...}, ...}
    summary = {}
    for txn in transactions:
        date = txn['date']
        category = txn['category__name'] or 'Uncategorized'
        amount = txn['total_amount']

        if date not in summary:
            summary[date] = {}
        summary[date][category] = amount

    context = {
        'summary': summary,
    }
    return render(request, 'cards/transactions_summary.html', context)