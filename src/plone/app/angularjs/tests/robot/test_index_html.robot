# bin/robot-server plone.app.angularjs.testing.PLONE_APP_ANGULARJS_ROBOT_TESTING
# bin/robot src/plone/app/angularjs/tests/robot/test_index_html.robot
*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***

Top Navigation
  Given a logged in admin
    and a folder  My Folder
   When I open the Plone AngularJS App
   Then the top navigation contains  My Folder

Portlet Navigation
  Given a logged in admin
    and a document  My Document
   When I open the Plone AngularJS App
   Then the portlet navigation contains  My Document

Portlet Navigation with nested Object
  Given a logged in admin
    and a document within a folder  My Document
   When I open the Plone AngularJS App
    and I click on the folder in the navigation
   Then the portlet navigation contains  My Document

Portal Root with Front Page
  Given a logged in admin
   When I open the Plone AngularJS App
   Then the page title is  Front Page
    and the page URL is  front-page


*** Keywords ***

a logged in admin
  Enable autologin as  Site Administrator
  Go to  ${PLONE_URL}

a document
  [Arguments]  ${title}  ${id}=document1
  Create content  type=Document  id=${id}  title=${title}

a folder
  [Arguments]  ${title}
  Create content  type=Folder  id=folder1  title=${title}

a document within a folder
  [Arguments]  ${title}
  ${folder_uid}  Create content  type=Folder  id=folder1  title=Folder 1
  Create content  type=Document  id=doc1  title=${title}  container=${folder_uid}

I open the Plone AngularJS App
  Create content  type=Document  id=front-page  title=Front Page
  Go To  ${PLONE_URL}
  Wait until page contains element  xpath=/html[@ng-app='ploneApp']

I click on the folder in the navigation
  Wait until element is visible  xpath=//div[@id='navigation-portlet-directive']//*[contains(text(), 'Folder 1')]
  Click Link  xpath=//div[@id='navigation-portlet-directive']//*[contains(text(), 'Folder 1')]

the top navigation contains
  [Arguments]  ${title}
  Capture Page Screenshot
  Wait until page contains element  css=#top-navigation-directive ul li a
  Wait until element is visible  css=#top-navigation-directive ul li a
  Element should contain  css=#top-navigation-directive  ${title}

the portlet navigation contains
  [Arguments]  ${title}
  Capture Page Screenshot
  Wait until element is visible  xpath=//div[@id='navigation-portlet-directive']//*[contains(text(), '${title}')]
  Page should contain element  xpath=//div[@id='navigation-portlet-directive']//*[contains(text(), '${title}')]

the page title is
  [Arguments]  ${title}
  Wait until page contains element  css=.jumbotron h1
  Wait until element is visible  css=.jumbotron h1
  Element should contain  css=.jumbotron h1  ${title}

the page URL is
  [Arguments]  ${id}
  Location Should Be  ${PLONE_URL}/${id}
