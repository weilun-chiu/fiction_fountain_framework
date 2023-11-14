import React, { Component } from "react";
import axios from "axios";


const getCsrfToken = () => {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    .split('=')[1];

  return cookieValue;
};

const csrfToken = getCsrfToken();
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      fictionFountainList: [],
    };
  }

  componentDidMount() {
    axios.get('/csrf/')
      .then((response) => {
        this.csrftoken = response.data.csrfToken;
        this.refreshList();
      })
      .catch((error) => {
        console.log(error);
      });
    window.addEventListener('scroll', this.handleScroll);
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.handleScroll);
  }

  handleScroll = () => {
    // Check if the user has scrolled to the bottom of the page
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
      // Call the function to increase reading progress or perform any other action
      this.increaseReadingProgress(1); // Change the argument based on the actual fictionFountainId
    }
  };

  increaseReadingProgress = (fictionFountainId) => {
    axios
      .post(`/api/fiction_fountains/${fictionFountainId}/increase_reading_progress/`, {}, {headers: {
        'X-CSRFToken': csrfToken,
      },})
      .then((res) => {
        console.log('Reading progress increased successfully.');
        // Call your refreshList method or update state as needed
        this.refreshList();
      })
      .catch((err) => console.error('Error increasing reading progress:', err));
  };

  resetReadingProgress = (fictionFountainId) => {
    axios
      .post(`/api/fiction_fountains/${fictionFountainId}/reset_reading_progress/`, {}, {headers: {
        'X-CSRFToken': csrfToken,
      },})
      .then((res) => {
        console.log('Reading progress resetd successfully.');
        // Call your refreshList method or update state as needed
        this.refreshList();
      })
      .catch((err) => console.error('Error increasing reading progress:', err));
  };

  handleButtonClickIncrReadProg = () => {
    // Call increaseReadingProgress with the appropriate fictionFountainId
    this.increaseReadingProgress(1); // Change the argument based on the actual fictionFountainId
  };

  handleButtonClickResetReadProg = () => {
    // Call increaseReadingProgress with the appropriate fictionFountainId
    this.resetReadingProgress(1); // Change the argument based on the actual fictionFountainId
  };


  refreshList = () => {
    axios
      .get("/api/fiction_fountains/")
      .then((res) => this.setState({ fictionFountainList: res.data }))
      .catch((err) => console.log(err));
  };

  renderItems = () => {
    this.refreshList();
    const newItems = this.state.fictionFountainList;

    return newItems.map((item) => (
      <div
        key={item.id}
        className="list-group-item d-flex flex-column align-items-start"
      >
        <span className={`todo-title mb-2`}>
          Genre: {item.genre}
        </span>
        <span className={`todo-title mb-2`}>
          People: {item.people}
        </span>
        <div>
          <p className="mb-1">Chapters:</p>
          {JSON.parse(item.chapters).map((chapter, index) => {
            // Check if the chapter index is less than or equal to reading_progress
            if (index <= item.reading_progress) {
              return (
                <pre key={index} className="list-group-item d-flex flex-column align-items-start max-w-screen-md mx-auto whitespace-pre-wrap">
                  {chapter.map((paragraph, pIndex) => (
                    <pre key={pIndex} dangerouslySetInnerHTML={{ __html: paragraph }} />
                  ))}
                </pre>
              );
            } else {
              // Return null for chapters that don't meet the condition
              return null;
            }
          })}
        </div>
      </div>
    ));    
  };

  render() {
    return (
      <main className="container">
        <h1 className="text-white text-uppercase text-center my-4">Todo app</h1>
        <div className="row">
          <div className="col-md-6 col-sm-10 mx-auto p-0">
            <div className="card p-3">
              <div className="mb-4">
                <button
                  className="btn btn-primary"
                  onClick={this.handleButtonClickIncrReadProg}
                >
                  Generate
                </button>
                <button
                  className="btn btn-primary"
                  onClick={this.handleButtonClickResetReadProg}
                >
                  Reset
                </button>
              </div>
              <ul className="list-group list-group-flush border-top-0">
                {this.renderItems()}
              </ul>
            </div>
          </div>
        </div>
      </main>
    );
  }
}

export default App;