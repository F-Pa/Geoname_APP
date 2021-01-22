from flask import Flask, render_template, request
from requete_hierarchy import hierarchy
from requete_lat_long import admin_loc

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#yDloPe.dkf\dR58\xec]/'


@app.route("/")
def home():
    return render_template("homepage.html")


@app.route('/', methods=['GET', 'POST'])
def geonaemid():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        if latitude == '' or longitude == '':
            message = 'Veuillez bien renseigner les champs'
            return render_template('/homepage.html', message=message)
        else:
            res = []
            for ti in admin_loc(float(latitude), float(longitude))[0:10]:
                res.append({'latitude': ti.get('latitude'), 'longitude': ti.get('longitude')})
            return render_template('/homepage.html', list=res)


@app.route('/geoname', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        geonameid = request.form['geonameid']
        if geonameid == '':
            message = 'Veuillez rentrer un champ valide'
            return render_template('/homepage.html', message=message)
        else:
            res = hierarchy(int(geonameid))
            return render_template('/homepage.html', tab=res)


if __name__ == "__main__":
    app.run(debug=True)