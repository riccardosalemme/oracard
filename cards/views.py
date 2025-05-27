from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, Card, Transaction, UserCard, TransactionCategory, UserCategory
from django.http import HttpResponse
from .generate_pdf import generate_qr_pdf

def instructions(request):
    return render(request, 'cards/instructions.html')

@login_required(login_url='login')
def bar(request):
    messages = []
    if request.method == 'POST':
        card_number = request.POST.get('code')
        c = Card.objects.filter(card_number=card_number).first()
        card = UserCard.objects.filter(card=c).first()

        if not card:
            messages.append("Card not found.")

        elif card.status != 'active':
            messages.append(f"Card is {card.status}. Reason: {card.notes if card.notes else 'No reason provided.'}")
        else:
            return redirect('cards_single', id=card.user.id)
       
    return render(request, 'cards/bar.html', {
        "messages": messages,
    })

@login_required(login_url='login')
def cards(request):
    q = request.GET.get('q')
    if q:
        users = User.objects.filter(name__icontains=q) | User.objects.filter(surname__icontains=q)
    else:
        users = User.objects.all()
    tr = Transaction.objects.filter(user_id__in=users)
    for user in users:
        user.cards = Card.objects.filter(usercard__user=user)
        user.transactions = tr.filter(user_id=user)
        user.total_spent = sum(transaction.amount for transaction in user.transactions)
        user.positive_balance = sum(transaction.amount for transaction in user.transactions if transaction.amount > 0)
        user.negative_balance = sum(transaction.amount for transaction in user.transactions if transaction.amount < 0)
        
    context = {
        "users": users
    }
    return render(request, 'cards/cards.html', context)

@login_required(login_url='login')
def cards_single(request, id):

    user = User.objects.filter(id=id).first()
    if not user:
        return render(request, 'cards/cards_single.html', {"error": "User not found"})
    
    dialog = []
    
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
            dialog.append("Transaction created successfully")
        else:
            dialog.append("No active card found for this user")
    
    
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
        "dialog": dialog,
    }
    return render(request, 'cards/cards_single.html', context)


    
@login_required(login_url='login')
def cards_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        
        
        user = User(name=name, surname=surname,)
        user.save()
    
        return redirect('cards_single', id=user.id)
    
    context = {
        "categories": UserCategory.objects.all(),
    }

    return render(request, 'cards/cards_create.html', context=context)

    
@login_required(login_url='login')
def cards_gen(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        card_id = request.POST.get('card_number')
        notes = request.POST.get('notes', '')

        if request.POST.get('disable_card') == 1:
            print("Disabling card for user:", user_id)
            # Disable all the cards
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
    