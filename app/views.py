import iRun
from flask import Flask as Flask,\
                  jsonify as FlaskJSONify,\
                  render_template as FlaskRender,\
                  request as FlaskRequest;               
from app import app 

@app.route('/') 
def index():
    return FlaskRender('myMap.html');

@app.route('/findRoute')
def findRoute():
    ###
    # Grab address from url
    ###
    startPt = FlaskRequest.args.get('s', '');
    endPt = FlaskRequest.args.get('e', '');
    runDist = float(FlaskRequest.args.get('d', ''));
    ###
    # Process the address
    ###
    print 'Inside /findRoute'
    print ('startPt is ').format(startPt)
    json = iRun.PathTestMashUp(startPt, endPt, runDist);
    ###
    # Check for bad address
    ###
    if json is None:
        print 'json is None'
        return FlaskJSONify({});
    ###
    # JSONify it
    ###
    return FlaskJSONify(json)

@app.route('/about')
def about():
    return FlaskRender('about.html');


@app.route('/<other>')
def other(other):
    return about();

###
### Script
###

if __name__ == '__main__':
    ###
    # Run Flask in debug, port 8000
    ###
    app.run(debug = True, port = 5000, host = '0.0.0.0');
