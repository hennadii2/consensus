import classNames from "classnames";
import Icon, { IconLoader } from "components/Icon";
import Tag from "components/Tag";
import { getAutocompleteQuerySuggestions } from "helpers/api";
import { setSynthesizeOn } from "helpers/setSynthesizeOn";
import { getAutocompleteEndpointParams } from "helpers/testingQueryParams";
import useLabels from "hooks/useLabels";
import useSearch from "hooks/useSearch";
import { useAppSelector } from "hooks/useStore";
import throttle from "lodash/throttle";
import { useRouter } from "next/router";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Autosuggest from "react-autosuggest";

const WAIT_BETWEEN_AUTOSUGGEST_REQUESTS_MSEC = 1000;

type SearchInputProps = {
  large?: boolean;
  trendings?: string[];
};

/**
 * @component SearchInput
 * @description Component for search input.
 * @example
 * return (
 *   <SearchInput large />
 * )
 */
const SearchInput = ({ large = false, trendings }: SearchInputProps) => {
  const router = useRouter();
  const [generalLabels] = useLabels("general");
  const [searchInputValue, setSearchInputValue] = useState<string>("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const isSearching = useAppSelector((state) => state.search.isSearching);
  const { handleSearch, authState } = useSearch();
  const inputRef = useRef<HTMLInputElement | null>(null);

  const onSubmit = useCallback(
    (e: any) => {
      e.preventDefault();
      inputRef.current?.blur();
      handleSearch(searchInputValue);
    },
    [searchInputValue, handleSearch, inputRef]
  );

  const onChangeSearchInput = useCallback((e: any, data?: any) => {
    setSearchInputValue(e.target.value);
  }, []);

  const onSuggestionSelected = useCallback(
    (_: any, { suggestion }: { suggestion: string }) => {
      inputRef.current?.blur();
      handleSearch(suggestion);
      setSearchInputValue(suggestion);
    },
    [handleSearch]
  );

  useEffect(() => {
    if (router?.query?.q) setSearchInputValue(router?.query?.q as string);
  }, [router?.query?.q]);

  const onSuggestionsRequested = useMemo(() => {
    const loadSuggestions = async ({
      value,
    }: {
      value: string;
    }): Promise<void> => {
      let suggestions: string[] = [];
      try {
        const params = getAutocompleteEndpointParams(router.query);
        const result = await getAutocompleteQuerySuggestions(value, params);
        suggestions = result.queries;
      } catch (error) {
        // do nothing
      }
      setSuggestions(suggestions);
    };
    return throttle(loadSuggestions, WAIT_BETWEEN_AUTOSUGGEST_REQUESTS_MSEC);
  }, [router?.query]);

  const onSuggestionsCleared = useCallback(() => {
    setSuggestions([]);
  }, []);

  const enterKeyHintStaticallyTypedToPassTypeCheck: "go" = "go";
  const inputProps = {
    value: searchInputValue,
    placeholder: generalLabels["search-input-placeholder"],
    onChange: onChangeSearchInput,
    ref: inputRef,
    type: "text",
    enterKeyHint: enterKeyHintStaticallyTypedToPassTypeCheck,
    className: classNames(
      "w-full rounded-full pt-3 sm:pt-[19px] pb-[11px] leading-[16.98px] sm:leading-6 text-sm sm:text-base sm:pb-[18px] pl-3 sm:pl-5 pr-20 md:pr-28 transition border border-transparent focus:border-green-600 hover:border-green-600 outline-none text-[#364B44] md:text-[#303A40] h-10 sm:h-14"
    ),
    "data-testid": "search-input",
  };

  return (
    <div>
      <form
        data-testid="search-input-form"
        className={classNames(
          "relative w-full sm:w-auto m-auto leading md:max-w-[444px] 2xl:max-w-[800px]",
          large && "flex-1 md:mx-24 lg:mx-24 xl:mx-auto sticky top-2",
          !large && "sm:w-[680px]"
        )}
        onSubmit={onSubmit}
      >
        <Autosuggest
          suggestions={suggestions}
          onSuggestionsFetchRequested={onSuggestionsRequested}
          onSuggestionsClearRequested={onSuggestionsCleared}
          getSuggestionValue={(suggestion: string) => suggestion}
          renderSuggestion={(suggestion: string) => <span>{suggestion}</span>}
          onSuggestionSelected={onSuggestionSelected}
          shouldRenderSuggestions={(value, reason) => true}
          inputProps={inputProps}
        />

        {searchInputValue && (
          <div
            className={`absolute top-0 h-full flex items-center right-14 md:right-20`}
          >
            <button
              data-testid="close-input"
              onClick={() => setSearchInputValue("")}
              type="button"
              className="bg-[#EDF0F2] hover:bg-gray-200 h-5 w-5 flex justify-center items-center rounded-full"
            >
              <Icon className="text-gray-500 h-4" name="x" />
            </button>
          </div>
        )}
        <button
          data-testid="search-button"
          id="search-button"
          type="submit"
          className="absolute top-0 bottom-0 right-4 md:right-6 flex items-center"
        >
          <div className="w-px h-3/5 bg-gray-200 mr-2 md:mr-4" />
          {isSearching ? (
            <div className="w-[36px] h-[36px] -mr-3">
              <IconLoader />
            </div>
          ) : (
            <img
              className="-mt-px h-6 w-6"
              src="/icons/input-search-icon.svg"
              alt="input-search-icon"
            />
          )}
        </button>
      </form>
      {trendings && (
        <div className="flex gap-3 justify-center items-center flex-wrap mb-16 mt-6">
          <p className="text-gray-500 font-medium">
            {generalLabels["try-searching"]}:
          </p>
          {trendings.map((item) => (
            <Tag
              key={item}
              q={item}
              onClick={(event) => {
                event.preventDefault();
                setSynthesizeOn();
                handleSearch(item);
              }}
            >
              {item}
            </Tag>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchInput;
