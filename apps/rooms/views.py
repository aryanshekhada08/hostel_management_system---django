from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Room, RoomAllocation
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()

def is_admin(user):
    return user.is_superuser

# 🟢 1. STANDARD ALLOCATE (Fixed)
@login_required
@user_passes_test(is_admin)
def allocate_room(request):

    if request.method == "POST":
        student_id = request.POST.get("student")
        room_id = request.POST.get("room")

        student = get_object_or_404(User, id=student_id)
        room = get_object_or_404(Room, id=room_id)

        # Prevent double allocation
        if RoomAllocation.objects.filter(student=student).exists():
            messages.error(request, "Student already has a room.")
            return redirect("room_dashboard") # Redirect to dashboard usually better

        # Check room availability
        if room.occupied < room.capacity: # Or use room.is_available() if you have that method
            # 1. Create the relationship
            RoomAllocation.objects.create(student=student, room=room)
            
            # 2. ✅ UPDATE THE COUNTER (This was missing)
            room.occupied += 1
            room.save()
            
            messages.success(request, "Room allocated successfully!")
        else:
            messages.error(request, "Room is full.")

        return redirect("room_dashboard")

    # If GET request, show dashboard usually, or specific allocate page
    return redirect("room_dashboard")


# 🔴 2. STANDARD DEALLOCATE (Fixed)
@login_required
@user_passes_test(is_admin)
def deallocate_room(request, allocation_id):
    allocation = get_object_or_404(RoomAllocation, id=allocation_id)
    
    room = allocation.room
    
    # ✅ Safety Check: Only decrease if > 0
    if room.occupied > 0:
        room.occupied -= 1
        room.save()

    allocation.delete()
    
    messages.success(request, "Student deallocated.")
    return redirect("room_dashboard")


# 🔵 3. DASHBOARD (Your filter logic was good, just cleaned up)
@login_required
@user_passes_test(is_admin)
def room_dashboard(request):

    search_query = request.GET.get("search", "").strip()
    room_filter = request.GET.get("room", "").strip()

    allocations = RoomAllocation.objects.select_related("student", "room").all()

    # 🔎 SEARCH LOGIC
    if search_query:
        allocations = allocations.filter(
            Q(student__email__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query)
        )

    # 🏠 ROOM FILTER
    if room_filter:
        allocations = allocations.filter(
            room__room_number=room_filter
        )

    # 📄 PAGINATION
    paginator = Paginator(allocations.order_by("-allocated_at"), 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Students without room
    allocated_students = RoomAllocation.objects.values_list("student", flat=True)
    students = User.objects.exclude(id__in=allocated_students)

    rooms = Room.objects.all()

    return render(request, "rooms/room_dashboard.html", {
        "rooms": rooms,
        "students": students,
        "page_obj": page_obj,
        "search_query": search_query,
        "room_filter": room_filter,
    })


# ⚡ 4. AJAX ALLOCATE (Fixed)
@require_POST
@login_required
@user_passes_test(is_admin)
def ajax_allocate_room(request):
    student_id = request.POST.get("student")
    room_id = request.POST.get("room")

    try:
        student = User.objects.get(id=student_id)
        room = Room.objects.get(id=room_id)
    except (User.DoesNotExist, Room.DoesNotExist):
         return JsonResponse({"status": "error", "message": "Invalid Student or Room."})

    if RoomAllocation.objects.filter(student=student).exists():
        return JsonResponse({"status": "error", "message": "Student already has a room."})

    if room.occupied >= room.capacity:
        return JsonResponse({"status": "error", "message": "Room is full."})

    # 1. Create Allocation
    RoomAllocation.objects.create(student=student, room=room)

    # 2. ✅ UPDATE THE COUNTER (This was missing)
    room.occupied += 1
    room.save()

    return JsonResponse({"status": "success", "message": "Room allocated successfully!"})


# ⚡ 5. AJAX DEALLOCATE (Fixed)
@require_POST
@login_required
@user_passes_test(is_admin)
def ajax_deallocate_room(request):
    # Note: You were looking for 'allocation_id' in POST, make sure JS sends it with that key
    # or you might be sending it in the URL. Assuming POST data here:
    allocation_id = request.POST.get("allocation_id")

    try:
        allocation = RoomAllocation.objects.get(id=allocation_id)
        room = allocation.room

        # ✅ Safety Check
        if room.occupied > 0:
            room.occupied -= 1
            room.save()

        allocation.delete()
        return JsonResponse({"status": "success", "message": "Deallocated successfully"})
        
    except RoomAllocation.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Allocation not found"})


@login_required
@user_passes_test(is_admin)
def add_room(request):
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        capacity = request.POST.get("capacity")

        # Check if room already exists to avoid crash
        if not Room.objects.filter(room_number=room_number).exists():
            Room.objects.create(
                room_number=room_number,
                capacity=capacity
            )
            messages.success(request, f"Room {room_number} added.")
        else:
            messages.error(request, f"Room {room_number} already exists.")

    return redirect("room_dashboard")