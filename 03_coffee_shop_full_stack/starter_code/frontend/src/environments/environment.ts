/* @DONE replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-31xxr8yqul4ks2qk.eu', // the auth0 domain prefix
    audience: 'http://localhost:8100', // the audience set for the auth0 app
    clientId: 'Jw2Xs18BQ3uWHTAm1HawPlgFM5JuVyLM', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application.
  },
};
