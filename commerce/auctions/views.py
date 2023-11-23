from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Comment, Bid


def listing(request, id):
    listingInfo = Listing.object.get(pk=id)
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    allComments = Comment.object.filter(listing=listingInfo)
    return render(request, "auctions/listing.html", {
        "listing": listingInfo,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments
    })


def removeWatchlist(request, id):
    listingInfo = Listing.objects.get(pk=id)
    currentUser = request.user
    listingInfo.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id)))


def addWatchlist(request, id):
    listingInfo = Listing.objects.get(pk=id)
    currentUser = request.user
    listingInfo.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id)))


def watchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def addComment(request, id):
    currentUser = request.user
    listingInfo = Listing.object.get(pk=id)
    message = request.POST["newComment"]

    newComment = Comment(
        author=currentUser,
        listing=listingInfo,
        message=message
    )
    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id)))


def addBid(request, id):
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    allComments = Comment.object.filter(listing=listingInfo)
    newBid = request.POST["newBid"]
    listingInfo = Listing.objects.get(pk=id)

    if int(newBid) > listingInfo.price.bid:
        updateBid = Bid(user=request.user, bid=int(newBid))
        updateBid.save()
        listingInfo.price = updateBid
        listingInfo.save()
        return render(request, "auctions/listing.html", {
            "listing": listingInfo,
            "message": "Bid was updated successfully",
            "update": True,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments
        })
    else:
        return render(request, "auctions/listing.html", {
            "listing": listingInfo,
            "message2": "Bid update failed",
            "update": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments
        })


def index(request):
    activeListing = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListing,
        "categories": allCategories
    })


def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        currentUser = request.user

        categoryInfo = Category.objects.get(categoryName=category)
        bid = Bid(bid=int(price), user=currentUser)
        bid.save()

        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageurl,
            price=bid,
            owner=currentUser,
            category=categoryInfo
        )
        newListing.save()

        return HttpResponseRedirect(reverse("index"))


def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListings = Listing.objects.filter(
            isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
