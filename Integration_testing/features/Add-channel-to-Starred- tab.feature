Feature: Add channel to *Starred* tab
	User needs to be able to mark channels with a star to label them as favorite for easy access

	Background: 
		Given that I am signed in on the system
			And that I am on any of the tabs (*My Channels*, *Starred*, *View only*, or *Content Library*)
			And I see a <channel> channel that is not starred (empty star)

	Scenario: Add chanel to *Starred* tab
		When I click the *star* button for the desired <channel>
		Then I see <channel> channel star is now full 
		When I click and open the *Starred* tab 
		Then I see <channel> channel is on the list

	Scenario: Remove chanel from *Starred* tab 
		Given I am on *My Channels*, *View only*, or *Public* tabs
			And I see a <channel> channel that is starred (full star)
		When I click the *star* button for the <channel>
		Then I see the star is now empty
		When I click and open the *Starred* tab 
		Then I see the list of channels
			But I don't see the <channel> channel on the list

	Scenario: Remove chanel directly from *Starred* tab 
		Given I am on *Starred* tabs
			And I see a <channel> channel on the list with a full star
		When I click the *star* button for the <channel>
		Then I don't see the <channel> channel any more