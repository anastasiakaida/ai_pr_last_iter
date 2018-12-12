import React, { Component } from 'react';
import logo from './logo.svg';
import stream from './stream.mov';
import './App.css';

class App extends Component {
    render() {

        const root = document.documentElement;

        return (
            <div className="App">
                <header className="App-header">

                </header>
                    <div id='content'>
                        <table style={{width:'100%', borderCollapse: 'collapse'}}>
                            <tbody>
                                <tr>
                                    <td colSpan='2' id='select_text'>Select object to recognize it from video</td>
                                </tr>
                                <tr>
                                    {/* put stream here  */}
                                    <td width='85%'><img id='stream' src='https://imagejournal.org/wp-content/uploads/bb-plugin/cache/23466317216_b99485ba14_o-panorama.jpg' /></td>
                                    <td>
                                        <table>
                                            <tbody style={{verticalAlign:'top'}}>
                                                    <tr>
                                                        <td><img id='mongoDb' style={{objectFit:'cover'}} src='https://imagejournal.org/wp-content/uploads/bb-plugin/cache/23466317216_b99485ba14_o-panorama.jpg'></img></td>
                                                    </tr>
                                                    <tr>
                                                        <td><button id='enlarge'>Enlarge image</button></td>
                                                    </tr>
                                                    <tr>
                                                        <td><button id='upload'>Upload file</button></td>
                                                    </tr>
                                                    <tr>
                                                        <td>
                                                            <nav>
                                                                <ul>
                                                                    <li>Object 1</li>
                                                                    <li>Object 2</li>
                                                                    <li>Object 3</li>
                                                                    <li>Object 4</li>
                                                                    <li>Object 5</li>
                                                                    <li>Object 6</li>
                                                                    <li>Object 7</li>
                                                                    <li>Object 8</li>
                                                                    <li>Object 9</li>
                                                                    <li>Object 10</li>
                                                                    <li>Object 11</li>
                                                                    <li>Object 12</li>
                                                                    <li>Object 13</li>
                                                                </ul>
                                                            </nav>
                                                        </td>
                                                    </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                            {/* Insert your MongoDb object here */}
                    </div>
            </div>
        );
    }
}

export default App;
