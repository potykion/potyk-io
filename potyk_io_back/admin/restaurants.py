from flask import flash, redirect, render_template, url_for
from flask_login import login_required

from potyk_io_back.admin.pres import admin_bp, flash_form_errors
from potyk_io_back.core.db import db
from potyk_io_back.potyk_io.restaurants.entities import (
    Restaurant,
    normalize_restaurant_tags,
    restaurant_vocab,
    seed_restaurants_if_empty,
)
from potyk_io_back.potyk_io.restaurants.forms import RestaurantForm


@admin_bp.route("/restaurants", methods=["GET", "POST"])
@login_required
def restaurants():
    seed_restaurants_if_empty()
    metros, tags = restaurant_vocab()
    form = RestaurantForm()

    if form.validate_on_submit():
        name = (form.name.data or "").strip()
        maps_url = (form.maps_url.data or "").strip()
        metro = (form.metro.data or "").strip()
        restaurant_tags = normalize_restaurant_tags(form.tags.data)

        if not name:
            flash("Укажи название", "error")
            return redirect(url_for("admin.restaurants"))
        if not maps_url:
            flash("Нужна ссылка на карту", "error")
            return redirect(url_for("admin.restaurants"))

        db.session.add(
            Restaurant(
                name=name,
                maps_url=maps_url,
                metro=metro,
                tags=restaurant_tags,
            )
        )
        db.session.commit()
        flash("Ресторан добавлен", "success")
        return redirect(url_for("potyk_io.restaurants"))

    if form.is_submitted():
        flash_form_errors(form)
        return render_template(
            "admin/restaurants.html",
            form=form,
            metros=metros,
            tags=tags,
        ), 400

    return render_template(
        "admin/restaurants.html",
        form=form,
        metros=metros,
        tags=tags,
    )
