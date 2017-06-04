#-*- coding: utf-8 -*-
#Venom.
from resources.lib.gui.hoster import cHosterGui
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib.util import cUtil
from resources.lib.config import cConfig
import re

SITE_IDENTIFIER = 'filmstreamingv2'
SITE_NAME = 'Filmstreamingv2'
SITE_DESC = 'Film streaming (Version 2) - Premier site de streaming film VF en HD'
 
URL_MAIN = 'http://www.filmstreamingv2.com/'

MOVIE_NEWS = (URL_MAIN+'xfsearch/', 'showMovies')
MOVIE_GENRES = (True, 'showGenres')

URL_SEARCH = (URL_MAIN + '?do=search&mode=advanced&subaction=search&titleonly=3&story=')
FUNCTION_SEARCH = 'showMovies'

def load():
    oGui = cGui()
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', URL_SEARCH[0])
    oGui.addDir(SITE_IDENTIFIER, 'showSearch', 'Recherche', 'search.png', oOutputParameterHandler)
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_NEWS[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_NEWS[1], 'Films (Derniers ajouts)', 'films_news.png', oOutputParameterHandler)
    
    oOutputParameterHandler = cOutputParameterHandler()
    oOutputParameterHandler.addParameter('siteUrl', MOVIE_GENRES[0])
    oGui.addDir(SITE_IDENTIFIER, MOVIE_GENRES[1], 'Films (Genres)', 'films_genres.png', oOutputParameterHandler)
    
    oGui.setEndOfDirectory()

def showSearch():
    oGui = cGui()

    sSearchText = oGui.showKeyBoard()
    if (sSearchText != False):
            sUrl = sSearchText
            showMovies(sUrl)
            oGui.setEndOfDirectory()
            return

def showGenres():
    oGui = cGui()
 
    liste = []
    liste.append( ['Action',URL_MAIN + 'xfsearch/action'] )
    liste.append( ['Animation',URL_MAIN + 'xfsearch/animation'] )
    liste.append( ['Aventure',URL_MAIN + 'xfsearch/aventure'] )
    liste.append( ['Biopic',URL_MAIN + 'xfsearch/biopic'] )
    liste.append( ['Comédie',URL_MAIN + 'xfsearch/Comedie'] )
    liste.append( ['Documentaire',URL_MAIN + 'xfsearch/documentaire'] )
    liste.append( ['Drame',URL_MAIN + 'xfsearch/drame'] )
    liste.append( ['Famille',URL_MAIN + 'xfsearch/famille'] )
    liste.append( ['Fantastique',URL_MAIN + 'xfsearch/fantastique'] )
    liste.append( ['Fiction',URL_MAIN + 'xfsearch/fiction'] )
    liste.append( ['Historique',URL_MAIN + 'xfsearch/historique'] )
    liste.append( ['Horreur',URL_MAIN + 'xfsearch/horreur'] )
    liste.append( ['Musical',URL_MAIN + 'xfsearch/musical'] )
    liste.append( ['Policier',URL_MAIN + 'xfsearch/policier'] )
    liste.append( ['Romance',URL_MAIN + 'xfsearch/romance'] )
    liste.append( ['Thriller',URL_MAIN + 'xfsearch/thriller'] )
    liste.append( ['Western',URL_MAIN + 'xfsearch/western'] )
               
    for sTitle,sUrl in liste:
        
        oOutputParameterHandler = cOutputParameterHandler()
        oOutputParameterHandler.addParameter('siteUrl', sUrl)
        oGui.addDir(SITE_IDENTIFIER, 'showMovies', sTitle, 'genres.png', oOutputParameterHandler)
       
    oGui.setEndOfDirectory()

def showMovies(sSearch = ''):
    oGui = cGui()
    if sSearch:
        sUrl = URL_SEARCH + sSearch
        
    else:
        oInputParameterHandler = cInputParameterHandler()
        sUrl = oInputParameterHandler.getValue('siteUrl')
        
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    sPattern = '<div class="hover-special"></div><img src="([^"]+)" alt="([^"]+)"><div class="hd720p">([^<]+)</div>.+?<div class="pipay1"><a href="([^"]+)"'

    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        total = len(aResult[1])
        dialog = cConfig().createDialog(SITE_NAME)
        for aEntry in aResult[1]:
            cConfig().updateDialog(dialog, total)
            if dialog.iscanceled():
                break
            sQual = aEntry[2]
            sQual = ' ('+ sQual + ')'
            sTitle = aEntry[1]
            sDisplayTitle = cUtil().DecoTitle(sTitle + sQual)
            sThumbnail = str(aEntry[0])
            if 'uploads/posts' in sThumbnail:
                sThumbnail = URL_MAIN + sThumbnail
            
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', str(aEntry[3]))
            oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
            oOutputParameterHandler.addParameter('sThumbnail',sThumbnail )
            oGui.addMovie(SITE_IDENTIFIER, 'showHosters', sDisplayTitle, '', sThumbnail, '', oOutputParameterHandler)
            
        cConfig().finishDialog(dialog)

        sNextPage = __checkForNextPage(sHtmlContent)
        if (sNextPage != False):
            oOutputParameterHandler = cOutputParameterHandler()
            oOutputParameterHandler.addParameter('siteUrl', sNextPage)
            oGui.addNext(SITE_IDENTIFIER, 'showMovies', '[COLOR teal]Next >>>[/COLOR]', oOutputParameterHandler)

    if not sSearch:
        oGui.setEndOfDirectory()

def __checkForNextPage(sHtmlContent):
    sPattern = '<span class="pnext"><a href="([^"]+)">Suivant</a></span>'
    oParser = cParser()
    aResult = oParser.parse(sHtmlContent, sPattern)

    if (aResult[0] == True):
        sUrl = aResult[1][0]
        #correction d'1 bug de leur site
        sUrl = sUrl.replace('xfsearch//page/2/','xfsearch/page/2/page/2/')
        return sUrl

    return False

def showHosters():

    oGui = cGui()
    oInputParameterHandler = cInputParameterHandler()
    sUrl = oInputParameterHandler.getValue('siteUrl')
    sMovieTitle = oInputParameterHandler.getValue('sMovieTitle')
    sThumbnail = oInputParameterHandler.getValue('sThumbnail')
    
    oRequestHandler = cRequestHandler(sUrl)
    sHtmlContent = oRequestHandler.request()
    
    oParser = cParser()

    sPattern = '<iframe.+?src="([^"]+)"'
    aResult = oParser.parse(sHtmlContent, sPattern)
    print aResult
    if (aResult[0] == True):
        for aEntry in aResult[1]:
            sHosterUrl = str(aEntry)
            sHosterUrl = sHosterUrl.replace('//ok.ru','https://ok.ru')   
            oHoster = cHosterGui().checkHoster(sHosterUrl)
            if (oHoster != False):
                oHoster.setDisplayName(sMovieTitle)
                oHoster.setFileName(sMovieTitle)
                cHosterGui().showHoster(oGui, oHoster, sHosterUrl, '')
            
             
    oGui.setEndOfDirectory()