import math
from datetime import date

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium


BANGALORE_CENTER = {"lat": 12.9716, "lon": 77.5946}


def init_state() -> None:
    if "listings" not in st.session_state:
        st.session_state.listings = [
            {
                "title": "2BHK near Manyata Tech Park",
                "lister_type": "Office Worker",
                "property_type": "Apartment",
                "rental_basis": ["Monthly"],
                "furnishing": "Semi-Furnished",
                "bedrooms": 2,
                "bathrooms": 2,
                "price_day": 1600,
                "price_month": 26000,
                "available_from": date(2026, 5, 1),
                "address": "Thanisandra Main Road, Bengaluru",
                "pincode": "560077",
                "latitude": 13.0466,
                "longitude": 77.6201,
                "description": "Ideal for 2-3 working professionals.",
            },
            {
                "title": "Student Friendly 1RK in BTM",
                "lister_type": "Student",
                "property_type": "Studio",
                "rental_basis": ["Daily", "Monthly"],
                "furnishing": "Furnished",
                "bedrooms": 1,
                "bathrooms": 1,
                "price_day": 850,
                "price_month": 14000,
                "available_from": date(2026, 4, 20),
                "address": "BTM 2nd Stage, Bengaluru",
                "pincode": "560076",
                "latitude": 12.9166,
                "longitude": 77.6101,
                "description": "Walkable distance to bus stop, great for students.",
            },
        ]



def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))



def listing_map(center_lat: float, center_lon: float, zoom_start: int = 12):
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    for listing in st.session_state.listings:
        popup = f"<b>{listing['title']}</b><br>{listing['property_type']}<br>₹{listing['price_month']}/month"
        folium.Marker(
            [listing["latitude"], listing["longitude"]],
            tooltip=listing["address"],
            popup=popup,
            icon=folium.Icon(color="blue", icon="home", prefix="fa"),
        ).add_to(fmap)
    return fmap



def page_list_property() -> None:
    st.header("List Property")
    st.caption("For students, office workers, and flatmates listing on daily/monthly basis.")

    st.subheader("Select Address from Map")
    picker_map = folium.Map(
        location=[BANGALORE_CENTER["lat"], BANGALORE_CENTER["lon"]],
        zoom_start=11,
    )
    folium.Marker(
        [BANGALORE_CENTER["lat"], BANGALORE_CENTER["lon"]],
        tooltip="Bengaluru center",
    ).add_to(picker_map)

    map_data = st_folium(picker_map, height=360, width=None, key="list-map")
    clicked = map_data.get("last_clicked") if map_data else None

    default_lat = clicked["lat"] if clicked else BANGALORE_CENTER["lat"]
    default_lon = clicked["lng"] if clicked else BANGALORE_CENTER["lon"]

    with st.form("property_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Property title")
            lister_type = st.selectbox("You are", ["Student", "Office Worker", "Owner", "Broker"])
            property_type = st.selectbox(
                "Property type",
                ["Apartment", "Studio", "Independent House", "Shared Room", "PG", "Villa"],
            )
            rental_basis = st.multiselect(
                "Rental basis",
                ["Daily", "Weekly", "Monthly"],
                default=["Monthly"],
            )
            furnishing = st.selectbox("Furnishing", ["Furnished", "Semi-Furnished", "Unfurnished"])
        with col2:
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=1)
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=1)
            price_day = st.number_input("Price per day (₹)", min_value=0, value=900, step=50)
            price_month = st.number_input("Price per month (₹)", min_value=0, value=15000, step=500)
            available_from = st.date_input("Available from", value=date.today())

        address = st.text_input("Address")
        pincode = st.text_input("Pincode")
        description = st.text_area("Description")

        lat_col, lon_col = st.columns(2)
        with lat_col:
            latitude = st.number_input("Latitude", value=float(default_lat), format="%.6f")
        with lon_col:
            longitude = st.number_input("Longitude", value=float(default_lon), format="%.6f")

        submitted = st.form_submit_button("Publish Property")

        if submitted:
            if not title or not address or not pincode or not rental_basis:
                st.error("Please fill title, address, pincode, and at least one rental basis.")
                return

            st.session_state.listings.append(
                {
                    "title": title,
                    "lister_type": lister_type,
                    "property_type": property_type,
                    "rental_basis": rental_basis,
                    "furnishing": furnishing,
                    "bedrooms": int(bedrooms),
                    "bathrooms": int(bathrooms),
                    "price_day": int(price_day),
                    "price_month": int(price_month),
                    "available_from": available_from,
                    "address": address,
                    "pincode": pincode,
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "description": description,
                }
            )
            st.success("Property listed successfully.")



def page_find_property() -> None:
    st.header("Find Property")
    st.caption("Filter by pincode, address search, or map area.")

    if not st.session_state.listings:
        st.info("No properties available yet.")
        return

    df = pd.DataFrame(st.session_state.listings)

    col1, col2, col3 = st.columns(3)
    with col1:
        pincode_filter = st.text_input("Filter by pincode")
    with col2:
        address_query = st.text_input("Address search")
    with col3:
        types = st.multiselect("Property type", sorted(df["property_type"].unique().tolist()))

    col4, col5 = st.columns(2)
    with col4:
        tenant_pref = st.selectbox("Listed by", ["Any", "Student", "Office Worker", "Owner", "Broker"])
    with col5:
        max_monthly = st.slider("Max monthly rent (₹)", 2000, 100000, 30000, step=1000)

    st.subheader("Map-based filter")
    filter_map = listing_map(BANGALORE_CENTER["lat"], BANGALORE_CENTER["lon"], zoom_start=11)
    map_data = st_folium(filter_map, height=360, width=None, key="find-map")
    clicked = map_data.get("last_clicked") if map_data else None
    radius_km = st.slider("Search radius around clicked point (km)", 1, 25, 5)

    filtered = df.copy()

    if pincode_filter.strip():
        filtered = filtered[filtered["pincode"].astype(str).str.contains(pincode_filter.strip(), case=False)]
    if address_query.strip():
        filtered = filtered[
            filtered["address"].astype(str).str.contains(address_query.strip(), case=False)
            | filtered["title"].astype(str).str.contains(address_query.strip(), case=False)
        ]
    if types:
        filtered = filtered[filtered["property_type"].isin(types)]
    if tenant_pref != "Any":
        filtered = filtered[filtered["lister_type"] == tenant_pref]
    filtered = filtered[filtered["price_month"] <= max_monthly]

    if clicked:
        clat, clon = clicked["lat"], clicked["lng"]
        filtered = filtered[
            filtered.apply(
                lambda row: haversine_km(clat, clon, float(row["latitude"]), float(row["longitude"]))
                <= radius_km,
                axis=1,
            )
        ]
        st.info(f"Map radius filter active at ({clat:.4f}, {clon:.4f}).")

    st.subheader(f"Matching Properties ({len(filtered)})")
    if filtered.empty:
        st.warning("No properties match the selected filters.")
        return

    for _, row in filtered.iterrows():
        with st.container(border=True):
            st.markdown(f"### {row['title']}")
            st.write(f"📍 {row['address']} ({row['pincode']})")
            st.write(
                f"🏠 {row['property_type']} • {row['bedrooms']}BHK/{row['bathrooms']} Bath • {row['furnishing']}"
            )
            st.write(f"💸 ₹{row['price_day']}/day • ₹{row['price_month']}/month")
            st.write(f"👤 Listed by: {row['lister_type']} | 📅 Available: {row['available_from']}")
            st.write(f"🗓 Rental basis: {', '.join(row['rental_basis'])}")
            if row["description"]:
                st.write(f"📝 {row['description']}")



def page_bangalore_map() -> None:
    st.header("Bangalore Rent Map (inspired layout)")
    st.caption("Visual map view similar to bengaluru.rent style browsing.")
    fmap = listing_map(BANGALORE_CENTER["lat"], BANGALORE_CENTER["lon"], zoom_start=11)
    st_folium(fmap, height=520, width=None, key="browse-map")



def main() -> None:
    st.set_page_config(page_title="Rental Share App", page_icon="🏠", layout="wide")
    init_state()

    st.title("🏠 Rental Share - Bengaluru")
    st.write("List and discover rental properties for students and office workers.")

    page = st.sidebar.radio("Navigation", ["List Property", "Find Property", "Bangalore Rent Map"])

    if page == "List Property":
        page_list_property()
    elif page == "Find Property":
        page_find_property()
    else:
        page_bangalore_map()


if __name__ == "__main__":
    main()
