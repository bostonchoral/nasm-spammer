require 'mechanize'

class NasmParser < Mechanize
  HOME = 'http://nasm.arts-accredit.org/'

  def process
    # it begins!
    get HOME

    # login
    click page.link_with(:text => /login/i)
    page.form_with(:action => /login/i) do |f|
      f.login = 'NAME'
      f.password = 'PW'
      f.click_button
    end

    # list members
    click page.link_with(:text => /directory/i)
    click page.link_with(:text => 'ACCREDITED INSTITUTIONAL MEMBERS')
    page.form_with(:action => /List_Accredited_Members/).click_button

    # fetch and process one member
    f = page.link_with(:href => /memberid/i)
    transact do
      click f
      data = page.search('td.maintxt td.maintxt').inner_html
      # TODO: regex fun
    end
    # TODO: every member
    # page.search('td.maintxt h2 a').each do |link|
    #    # puts link.content
    #    # click link[:href]
    #    # p page./ 'td.maintxt'
    # end


    click page.link_with(:text => /logout/i)
  end
end

NasmParser.new.process
