31b7b960-7a36-4a42-be15-eeba4d0d376a
read in content by weight^2

mind listen
mind learn
    --parser = verse, paragraph, pdf, web-url
                parser preserve Proper Names
    --tag = verse, journal, iching  (bloom filter)
    --ignore = regex
    --substitute = regex
    --data = block-of-data

    can I turn a bithash of tags + hash of token into a bloom filter?

mind show
    stats (show total words, first-time, last-time, time distribution curve)
    token <glob> (show next-word-count, first-time, last-time, time distribution curve)

mind think
    --mood (weights and variables and logic)
    --tag
    --ignore = regex
    --substitute = regex
    


flows through the view
one thought at a time alternating between

anatman.org = generated from trained prajna.io
prajnaparamita.org = read from fragments or journal (or commentary?)



lines offset by +- using a random wave generator
   formula for a bell curve
https://www.thoughtco.com/normal-distribution-bell-curve-formula-3126278
https://9to5science.com/formula-for-skewed-bell-curve

distribution of n number of j-sided dice with skew

next thought
folloing a References= or SeeAlso=
or matches a Source.ID= or Source.Source.ID= or ...
or matches Subject=

or search on random term
50% top 1 match
25% top 2 match
12.5% top  3 match
...



word x word grid of n-count / total-words (by cell)
feed through content
and the grid constantly changes

stored as files named hash(token)
each file db of nextword : ( n-count , time-created )

token = ( mind-type = (prose | verse) & (not-journal | journal) ) + (bos | bob | bol)  + word + punctuation + ( eol | eob | eof )
                                        how end-of-stream?

special token for eol to freq of eob
token for eob to freq of eos
special token for eos (end of stream) to next (following Ref, source, subject etc.)


another table of time-created and total-words-heard, prose-count, verse-count, journal-count

so frequency = n-count / (time-created join to total-words-heard)


rhyming verse
build lines backward
