# -*- coding: utf-8; -*-

import gherkin
from gherkin import OldLexer, Lexer, Parser, Ast


def test_lex_test_eof():
    "lex_text() Should be able to find EOF"

    # Given a lexer that takes '' as the input string
    lexer = gherkin.Lexer('')

    # When we try to lex any text from ''
    new_state = lexer.lex_text()

    # Then we see we've got to EOF and that new state is nil
    lexer.tokens.should.equal([(gherkin.TOKEN_EOF, '')])
    new_state.should.be.none


def test_lex_text():
    "lex_text() Should be able to find text before EOF"

    # Given a lexer that takes some text as input string
    lexer = gherkin.Lexer('some text')

    # When we lex it
    new_state = lexer.lex_text()

    # Then we see we found both the text and the EOF token
    lexer.tokens.should.equal([
        (gherkin.TOKEN_TEXT, 'some text'),
        (gherkin.TOKEN_EOF, '')
    ])

    # And the new state is nil
    new_state.should.be.none


def test_lex_hash_with_text():
    "lex_text() Should stop lexing at # (we found a comment!)"

    # Given a lexer with some text and some comment
    lexer = gherkin.Lexer(' some text # random comment')

    # When the input is lexed through the text lexer
    new_state = lexer.lex_text()

    # Then we see the following token on the output list
    lexer.tokens.should.equal([
        (gherkin.TOKEN_TEXT, 'some text '),
    ])

    # And that the next state will lex comments
    new_state.should.equal(lexer.lex_comment)


def test_lex_comment():
    "lex_comment() Should stop lexing at \\n"

    # Given a lexer loaded with some comments
    lexer = gherkin.Lexer('   random comment')

    # When We lex the input text
    new_state = lexer.lex_comment()

    # Then we see the comment above was captured
    lexer.tokens.should.equal([
        (gherkin.TOKEN_COMMENT, 'random comment'),
    ])

    # And that new state is lex_text()
    new_state.should.equal(lexer.lex_text)


def test_lex_comment_meta_label():
    "lex_comment() Should stop lexing at : (we found a label)"

    # Given a lexer loaded with a comment that contains a label
    lexer = gherkin.Lexer('     metadata: test')

    # When we lex the comment
    new_state = lexer.lex_comment()

    # Then we see that a label was found
    lexer.tokens.should.equal([
        (gherkin.TOKEN_META_LABEL, 'metadata'),
    ])

    # And that new state is going to read the value of the variable we
    # just found
    new_state.should.equal(lexer.lex_comment_metadata_value)


def test_lex_comment_metadata_value():
    "lex_comment_metadata_value() Should stop lexing at \n"

    # Given a lexer loaded with the value of a label and a new line
    # with more text
    lexer = gherkin.Lexer(' test value\nblah')

    # When we lex the input string
    new_state = lexer.lex_comment_metadata_value()

    # Then we see that only the value
    lexer.tokens.should.equal([
        (gherkin.TOKEN_META_VALUE, 'test value'),
    ])

    # And we also see that the next
    new_state.should.equal(lexer.lex_text)


def test_lex_comment_full():
    "Lexer.run() Should be able to process metadata in comments"

    # Given a lexer loaded with comments containing a metadata field
    lexer = gherkin.Lexer('some text # metadata-field: blah-value\ntext')

    # When I run the lexer
    tokens = lexer.run()

    # Then I see the tokens collected match some text, a field, more
    # text and EOF
    tokens.should.equal([
        (gherkin.TOKEN_TEXT, 'some text '),
        (gherkin.TOKEN_META_LABEL, 'metadata-field'),
        (gherkin.TOKEN_META_VALUE, 'blah-value'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'text'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_label():
    "Lexer.run() Should be able to parse a label with some text"

    # Given a lexer loaded with a feature
    lexer = gherkin.Lexer(
        'Feature: A cool feature\n  some more text\n  even more text')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the token list matches the label, text, text EOF
    # sequence
    tokens.should.equal([
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'A cool feature'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'some more text'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'even more text'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_labels():
    "Lexer.run() Should be able to tokenize a feature with a scenario"

    # Given a lexer with a more complete feature+scenario
    lexer = gherkin.Lexer('''

Feature: Some descriptive text
  In order to parse a Gherkin file
  As a parser
  I want to be able to parse scenarios

  Even more text

  Scenario: The user wants to describe a feature
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see it was broken down into the right list of tokens
    tokens.should.equal([
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'Some descriptive text'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'In order to parse a Gherkin file'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'As a parser'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'I want to be able to parse scenarios'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Even more text'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Scenario'),
        (gherkin.TOKEN_TEXT, 'The user wants to describe a feature'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_text_with_steps():
    "Lexer.run() Should be able to tokenize steps"

    # Given a lexer loaded with feature+background+scenario+steps
    lexer = gherkin.Lexer('''\
Feature: Feature title
  feature description
  Background: Some background
    about the problem
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that everything, including the steps was properly
    # tokenized
    tokens.should.equal([
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'Feature title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'feature description'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Background'),
        (gherkin.TOKEN_TEXT, 'Some background'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'about the problem'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Scenario'),
        (gherkin.TOKEN_TEXT, 'Scenario title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Given first step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'When second step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Then third step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_load_languages():
    "Lexer.run() Should be able to parse different languages"

    # Given the following lexer instance loaded with another language
    lexer = gherkin.Lexer('''# language: pt-br

    Funcionalidade: Interpretador para gherkin
      Para escrever testes de aceitação
      Como um programador
      Preciso de uma ferramenta de BDD
    Contexto:
      Dado que a variavel "X" contém o número 2
    Cenário: Lanche
      Dada uma maçã
      Quando mordida
      Então a fome passa
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then the following list of tokens is generated
    tokens.should.equal([
        (gherkin.TOKEN_META_LABEL, 'language'),
        (gherkin.TOKEN_META_VALUE, 'pt-br'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Funcionalidade'),
        (gherkin.TOKEN_TEXT, 'Interpretador para gherkin'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Para escrever testes de aceitação'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Como um programador'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Preciso de uma ferramenta de BDD'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Contexto'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Dado que a variavel "X" contém o número 2'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Cenário'),
        (gherkin.TOKEN_TEXT, 'Lanche'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Dada uma maçã'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Quando mordida'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Então a fome passa'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_tables():
    "Lexer.run() Should be able to lex tables"

    lexer = gherkin.Lexer('''\
  Examples:
    | column1 | column2 |
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the scenario outline case was properly parsed
    tokens.should.equal([
        (gherkin.TOKEN_LABEL, 'Examples'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, 'column1'),
        (gherkin.TOKEN_TABLE_COLUMN, 'column2'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, ''),
    ])


def test_lex_tables_full():
    "Lexer.run() Should be able to lex scenario outlines"

    lexer = gherkin.Lexer('''\
  Feature: gherkin has steps with examples
  Scenario Outline: Add two numbers
    Given I have <input_1> and <input_2> the calculator
    When I press Sum!
    Then the result should be <output> on the screen
  Examples:
    | input_1 | input_2 | output |
    | 20      | 30      | 50     |
    | 0       | 40      | 40     |
''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see the scenario outline case was properly parsed
    tokens.should.equal([
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'gherkin has steps with examples'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Scenario Outline'),
        (gherkin.TOKEN_TEXT, 'Add two numbers'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Given I have <input_1> and <input_2> the calculator'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'When I press Sum!'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Then the result should be <output> on the screen'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Examples'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, 'input_1'),
        (gherkin.TOKEN_TABLE_COLUMN, 'input_2'),
        (gherkin.TOKEN_TABLE_COLUMN, 'output'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, '20'),
        (gherkin.TOKEN_TABLE_COLUMN, '30'),
        (gherkin.TOKEN_TABLE_COLUMN, '50'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, '0'),
        (gherkin.TOKEN_TABLE_COLUMN, '40'),
        (gherkin.TOKEN_TABLE_COLUMN, '40'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_lex_tables_within_steps():
    "Lexer.run() Should be able to lex example tables from steps"

    # Given a lexer loaded with steps that contain example tables
    lexer = gherkin.Lexer('''\
	Feature: Check models existence
		Background:
	   Given I have a garden in the database:
	      | @name  | area | raining |
	      | Secret Garden | 45   | false   |
	    And I have gardens in the database:
	      | name            | area | raining |
	      | Octopus' Garden | 120  | true    |
    ''')

    # When we run the lexer
    tokens = lexer.run()

    # Then we see that steps that contain : will be identified as
    # labels
    tokens.should.equal([
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'Check models existence'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Background'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Given I have a garden in the database'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, '@name'),
        (gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, 'Secret Garden'),
        (gherkin.TOKEN_TABLE_COLUMN, '45'),
        (gherkin.TOKEN_TABLE_COLUMN, 'false'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'And I have gardens in the database'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, 'name'),
        (gherkin.TOKEN_TABLE_COLUMN, 'area'),
        (gherkin.TOKEN_TABLE_COLUMN, 'raining'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TABLE_COLUMN, 'Octopus\' Garden'),
        (gherkin.TOKEN_TABLE_COLUMN, '120'),
        (gherkin.TOKEN_TABLE_COLUMN, 'true'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, '')
    ])


def test_parse_metadata_syntax_error():

    parser = Parser([
        (gherkin.TOKEN_META_LABEL, 'language'),
        (gherkin.TOKEN_TEXT, 'pt-br'),
    ])

    parser.parse_metadata.when.called.should.throw(
        SyntaxError, 'No value found for the meta-field `language\'')


def test_parse_metadata():

    parser = Parser([
        (gherkin.TOKEN_META_LABEL, 'language'),
        (gherkin.TOKEN_META_VALUE, 'pt-br'),
    ])

    parser.parse_metadata()

    parser.output.should.equal([
        Ast.Metadata('language', 'pt-br'),
    ])


def test_parse_metadata():

    parser = Parser([
        (gherkin.TOKEN_META_LABEL, 'language'),
        (gherkin.TOKEN_META_VALUE, 'pt-br'),
    ])

    metadata = parser.parse_metadata()

    metadata.should.equal(Ast.Metadata('language', 'pt-br'))


def test_parse_empty_title():

    parser = Parser([
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'more text after title'),
    ])

    feature = parser.parse_title()

    feature.should.equal(Ast.Text(''))


def test_parse_title():

    parser = Parser([
        (gherkin.TOKEN_TEXT, 'Scenario title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
    ])

    feature = parser.parse_title()

    feature.should.equal(Ast.Text('Scenario title'))


def teste_parse_scenarios():

    parser = Parser([
        (gherkin.TOKEN_LABEL, 'Scenario'),
        (gherkin.TOKEN_TEXT, 'Scenario title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Given first step'),
    ])

    feature = parser.parse_scenarios()

    feature.should.equal([Ast.Scenario(
        title=Ast.Text('Scenario title'),
        steps=[Ast.Step(Ast.Text('Given first step'))],
    )])


def test_parse_not_starting_with_feature():

    parser = gherkin.Parser(gherkin.Lexer('''
Scenario: Scenario title
  Given first step
   When second step
   Then third step
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError,
        "Feature expected in the beginning of the file, "
        "found `Scenario' though.")


def test_parse_feature_two_backgrounds():

    parser = gherkin.Parser(gherkin.Lexer('''
Feature: Feature title
  feature description
  Background: Some background
    about the problem
  Background: Some other background
    will raise an exception
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError, "`Background' should not be declared here, Scenario expected")


def test_parse_feature_background_wrong_place():

    parser = gherkin.Parser(gherkin.Lexer('''
Feature: Feature title
  feature description
  Scenario: Scenario title
    Given first step
     When second step
     Then third step
  Background: Some background
    about the problem
    ''').run())

    parser.parse_feature.when.called.should.throw(
        SyntaxError, "`Background' should not be declared here, Scenario expected")


def test_parse_feature():

    parser = Parser([
        (gherkin.TOKEN_LABEL, 'Feature'),
        (gherkin.TOKEN_TEXT, 'Feature title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'feature description'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Background'),
        (gherkin.TOKEN_TEXT, 'Some background'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'about the problem'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Scenario'),
        (gherkin.TOKEN_TEXT, 'Scenario title'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Given first step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_LABEL, 'Scenario'),
        (gherkin.TOKEN_TEXT, 'Another scenario'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'Given this step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_TEXT, 'When we take another step'),
        (gherkin.TOKEN_NEWLINE, '\n'),
        (gherkin.TOKEN_EOF, ''),
    ])

    feature = parser.parse_feature()

    feature.should.equal(Ast.Feature(
        title=Ast.Text('Feature title'),
        description=Ast.Text('feature description'),
        background=Ast.Background(
            Ast.Text('Some background'),
            Ast.Text('about the problem')),
        scenarios=[
            Ast.Scenario(title=Ast.Text('Scenario title'),
                         steps=[Ast.Step(Ast.Text('Given first step'))]),
            Ast.Scenario(title=Ast.Text('Another scenario'),
                         steps=[Ast.Step(Ast.Text('Given this step')),
                                Ast.Step(Ast.Text('When we take another step'))]),
        ],
    ))


def test_read_metadata():
    "It should be possible to read metadata from feature files"

    # Given that I have an instance of a lexer
    lexer = OldLexer('en')

    # When I scan a feature with lang and encoding
    nodes = lexer.scan('''# language: en
# encoding: utf-8

Feature: My lame feature
     My lame description
''')

    # Then I see that the corresponding node list is correct
    nodes.should.equal([
        ('metadata', ('language', 'en')),
        ('metadata', ('encoding', 'utf-8')),
        ('identifier', ('Feature', 'My lame feature')),
        ('text', 'My lame description'),
    ])


def test_lexer_single_feature():
    "The lexer should be able to emit tokens for the Feature identifier"

    # Given an instance of a localized lexes
    lexer = OldLexer('')

    # When I scan a feature description
    nodes = lexer.scan('''Feature: My Feature
  Description of my feature in
  multiple lines
''')

    # Then I see the corresponding node list is correct
    nodes.should.equal([
        ('identifier', ('Feature', 'My Feature')),
        ('text', 'Description of my feature in'),
        ('text', 'multiple lines'),
    ])


def test_feature_with_comments():
    "It should be possible to add comments to features and text"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('en')

    # When I scan a feature description with comments
    nodes = lexer.scan('''\
# Some nice comments
# Some more nice comments

Feature: Name     # More comments
  Description     # Desc
''')

    # Then I see that the corresponding node list is correct
    nodes.should.equal([
        ('comment', "Some nice comments"),
        ('comment', "Some more nice comments"),
        ('identifier', ('Feature', 'Name')),
        ('comment', 'More comments'),
        ('text', 'Description'),
        ('comment', 'Desc'),
    ])


def test_feature_with_background():
    "It should be possible to declare a background for a feature"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('')

    # When I scan a feature with a background
    nodes = lexer.scan('''\
Feature: Random
  Description with
  two lines

  Background:
    Given a feature
      And a background
     Then I eat some cookies
''')

    # Then I see that the corresponding node list is correct
    nodes.should.equal([
        ('identifier', ('Feature', 'Random')),

        ('text', 'Description with'),
        ('text', 'two lines'),
        ('identifier', ('Background', '')),

        ('step', ('Given', 'a feature')),
        ('step', ('And', 'a background')),
        ('step', ('Then', 'I eat some cookies')),
    ])


def test_random_spaces_in_syntax():
    "It should be possible to use any syntax when declaring steps"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('')

    # When I scan the description of a feature with a scenario with a list of
    # weirdly indented steps
    nodes = lexer.scan('''\
Feature: Paladin
  Coder that cleans stuff up

  Scenario: Fight the evil
    Given that I have super powers
      And a nice costume
   When I see bad code
     Then I should rewrite it to look good

  Scenario: Eat cookies
    Given that I'm hungry
     When I open the cookie jar
     Then I should eat a delicious cookie
''')

    # Then I see that the corresponding node list is correct
    nodes.should.equal([
        ('identifier', ('Feature', 'Paladin')),
        ('text', 'Coder that cleans stuff up'),

        ('identifier', ('Scenario', 'Fight the evil')),

        ('step', ('Given', 'that I have super powers')),
        ('step', ('And', 'a nice costume')),
        ('step', ('When', 'I see bad code')),
        ('step', ('Then', 'I should rewrite it to look good')),

        ('identifier', ('Scenario', 'Eat cookies')),

        ('step', ('Given', 'that I\'m hungry')),
        ('step', ('When', 'I open the cookie jar')),
        ('step', ('Then', 'I should eat a delicious cookie')),
    ])


def test_tables():
    "It should be possible to declare tables in steps"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('')

    # When I scan the description of a feature with a scenario outlines
    nodes = lexer.scan('''\
Feature: Name

  Scenario: Hacker list
    Given that I have a list of hackers:
      | name    | email             |
      | lincoln | lincoln@wlabs.com |
      | gabriel | gabriel@wlabs.com |
    When I create them as "super-ultra-users"
''')

    # Then I see that the correspond list of tokens is right
    nodes.should.equal([
        ('identifier', ('Feature', 'Name')),

        ('identifier', ('Scenario', 'Hacker list')),

        ('step', ('Given', 'that I have a list of hackers')),
        ('row', ('name', 'email')),
        ('row', ('lincoln', 'lincoln@wlabs.com')),
        ('row', ('gabriel', 'gabriel@wlabs.com')),
        ('step', ('When', 'I create them as "super-ultra-users"')),
    ])


def test_scenario_outlines():
    "It should be possible to declare a complete scenario outline"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('en')

    # When I scan the description of a feature with a scenario outlines
    nodes = lexer.scan('''\
Feature: Name

  Scenario Outline: Hacker list
    Given I have the users:
      | name    | email             |
      | lincoln | lincoln@wlabs.com |
      | gabriel | gabriel@wlabs.com |
    When   I create them as "<role>"
    Then   they have permission to "edit <content type>"

  Examples:
    | role        | content type |
    | superuser   | posts        |
    | normal user | comments     |
''')

    # Then I see that the correspond list of tokens is right
    nodes.should.equal([
        ('identifier', ('Feature', 'Name')),

        ('identifier', ('Scenario Outline', 'Hacker list')),

        ('step', ('Given', 'I have the users')),
        ('row', ('name', 'email')),
        ('row', ('lincoln', 'lincoln@wlabs.com')),
        ('row', ('gabriel', 'gabriel@wlabs.com')),

        ('step', ('When', 'I create them as "<role>"')),
        ('step', ('Then', 'they have permission to "edit <content type>"')),
        ('identifier', ('Examples', '')),
        ('row', ('role', 'content type')),
        ('row', ('superuser', 'posts')),
        ('row', ('normal user', 'comments')),
    ])


def test_tags():
    "It should be possible to read tags"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('')

    # When I scan the description of a feature with some tags
    nodes = lexer.scan('''\
@tag1 @tag|2
Feature: Name

  @tag.3 @tag-4
  Scenario: Hacker list
    Given that I have a list of hackers:
      | name    | email             |
      | lincoln | lincoln@wlabs.com |
      | gabriel | gabriel@wlabs.com |
    When I create them as "super-ultra-users"
''')

    # Then I see that the correspond list of tokens is right
    nodes.should.equal([
        ('tag', 'tag1'),
        ('tag', 'tag|2'),
        ('identifier', ('Feature', 'Name')),

        ('tag', 'tag.3'),
        ('tag', 'tag-4'),
        ('identifier', ('Scenario', 'Hacker list')),

        ('step', ('Given', 'that I have a list of hackers')),
        ('row', ('name', 'email')),
        ('row', ('lincoln', 'lincoln@wlabs.com')),
        ('row', ('gabriel', 'gabriel@wlabs.com')),
        ('step', ('When', 'I create them as "super-ultra-users"')),
    ])


def test_multiline_strings():
    "It should be possible to declare multiline strings in steps"

    # Given that I have a tasty instance of a delicious localized lexer
    lexer = OldLexer('')

    # When I scan the description of a feature with some multiline strings
    nodes = lexer.scan('''\
Feature: Create new files

  As a user
  I need to create files

  Background:
    Given an empty directory
    When I create the file "blah" with:
      """
      This is the content of my file
      there are multiple lines here, can
      ya see? :)
      """
''')

    # Then I see that the correspond list of tokens is right
    nodes.should.equal([
        ('identifier', ('Feature', 'Create new files')),
        ('text', 'As a user'),
        ('text', 'I need to create files'),
        ('identifier', ('Background', '')),
        ('step', ('Given', 'an empty directory')),
        ('step', ('When', 'I create the file "blah" with')),
        ('text', ('This is the content of my file\n'
                  'there are multiple lines here, can\n'
                  'ya see? :)')),
    ])
